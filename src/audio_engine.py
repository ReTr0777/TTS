import asyncio
import io
import threading
import traceback
import tempfile
import os
from typing import List, Dict, Optional, Tuple, Callable
import sounddevice as sd
import soundfile as sf
import numpy as np
import edge_tts
import pyttsx3

from src.config import config

POPULAR_VOICES = [
    # US English
    {"id": "en-US-ChristopherNeural", "name": "Christopher (US Male - Deep & Natural)", "lang": "en-US", "gender": "Male"},
    {"id": "en-US-JennyNeural", "name": "Jenny (US Female - Friendly & Clear)", "lang": "en-US", "gender": "Female"},
    {"id": "en-US-GuyNeural", "name": "Guy (US Male - Casual & Expressive)", "lang": "en-US", "gender": "Male"},
    {"id": "en-US-AriaNeural", "name": "Aria (US Female - Crisp & Professional)", "lang": "en-US", "gender": "Female"},
    {"id": "en-US-EricNeural", "name": "Eric (US Male - Warm)", "lang": "en-US", "gender": "Male"},
    {"id": "en-US-MichelleNeural", "name": "Michelle (US Female - Upbeat)", "lang": "en-US", "gender": "Female"},
    # UK English
    {"id": "en-GB-RyanNeural", "name": "Ryan (UK Male - British Accent)", "lang": "en-GB", "gender": "Male"},
    {"id": "en-GB-SoniaNeural", "name": "Sonia (UK Female - British Accent)", "lang": "en-GB", "gender": "Female"},
    # AU / CA
    {"id": "en-AU-WilliamMultilingualNeural", "name": "William (AU Male - Australian)", "lang": "en-AU", "gender": "Male"},
    {"id": "en-AU-NatashaNeural", "name": "Natasha (AU Female - Australian)", "lang": "en-AU", "gender": "Female"},
    {"id": "en-CA-LiamNeural", "name": "Liam (CA Male - Canadian)", "lang": "en-CA", "gender": "Male"},
    # Dutch
    {"id": "nl-NL-MaartenNeural", "name": "Maarten (NL Male - Dutch)", "lang": "nl-NL", "gender": "Male"},
    {"id": "nl-NL-FennaNeural", "name": "Fenna (NL Female - Dutch)", "lang": "nl-NL", "gender": "Female"},
    # Japanese
    {"id": "ja-JP-KeitaNeural", "name": "Keita (JP Male - Japanese)", "lang": "ja-JP", "gender": "Male"},
    {"id": "ja-JP-NanamiNeural", "name": "Nanami (JP Female - Japanese)", "lang": "ja-JP", "gender": "Female"},
    # Spanish
    {"id": "es-ES-AlvaroNeural", "name": "Alvaro (ES Male - Spanish)", "lang": "es-ES", "gender": "Male"},
    {"id": "es-ES-ElviraNeural", "name": "Elvira (ES Female - Spanish)", "lang": "es-ES", "gender": "Female"},
    # German & French
    {"id": "de-DE-ConradNeural", "name": "Conrad (DE Male - German)", "lang": "de-DE", "gender": "Male"},
    {"id": "fr-FR-HenriNeural", "name": "Henri (FR Male - French)", "lang": "fr-FR", "gender": "Male"},
]

def resample_audio(audio_data: np.ndarray, orig_sr: int, target_sr: int) -> np.ndarray:
    """Fast linear interpolation resampling for numpy arrays."""
    if orig_sr == target_sr or len(audio_data) == 0:
        return audio_data
    
    num_samples = int(len(audio_data) * target_sr / orig_sr)
    old_indices = np.linspace(0, len(audio_data) - 1, len(audio_data))
    new_indices = np.linspace(0, len(audio_data) - 1, num_samples)
    
    if audio_data.ndim == 1:
        return np.interp(new_indices, old_indices, audio_data).astype(np.float32)
    elif audio_data.ndim == 2:
        resampled_cols = [
            np.interp(new_indices, old_indices, audio_data[:, c])
            for c in range(audio_data.shape[1])
        ]
        return np.column_stack(resampled_cols).astype(np.float32)
    return audio_data

class AudioEngine:
    def __init__(self):
        self._is_speaking = False
        self._stop_event = threading.Event()
        self.on_state_change: Optional[Callable[[bool], None]] = None

    @property
    def is_speaking(self) -> bool:
        return self._is_speaking

    def list_output_devices(self) -> List[Dict]:
        """Returns clean list of output devices (WASAPI, DirectSound, MME). Excludes unstable WDM-KS."""
        try:
            devices = sd.query_devices()
            hostapis = sd.query_hostapis()
            default_out = sd.default.device[1]
            out_list = []
            
            # Host API priority order (WDM-KS is excluded because it causes PaErrorCode -9996)
            api_priority = {"Windows WASAPI": 1, "Windows DirectSound": 2, "MME": 3}
            
            raw_devices = []
            for i, d in enumerate(devices):
                if d['max_output_channels'] > 0:
                    api_name = hostapis[d['hostapi']]['name']
                    # Skip Kernel Streaming devices
                    if "wdm-ks" in api_name.lower():
                        continue
                    raw_devices.append((api_priority.get(api_name, 99), i, d, api_name))
                    
            raw_devices.sort(key=lambda x: (x[0], x[1]))
            
            for _, i, d, api_name in raw_devices:
                out_list.append({
                    "id": i,
                    "name": d['name'],
                    "api": api_name,
                    "full_label": f"{d['name']} [{api_name}]",
                    "channels": d['max_output_channels'],
                    "samplerate": int(d['default_samplerate']),
                    "is_default": (i == default_out)
                })
            return out_list
        except Exception as e:
            print(f"[AudioEngine] Error querying output devices: {e}")
            return []

    def resolve_device_id(self, identifier, is_output=True) -> Optional[int]:
        """Finds device index by integer ID or fuzzy name match."""
        if identifier is None or identifier == "":
            return None
        
        devices = self.list_output_devices() if is_output else []
        
        # If integer id
        if isinstance(identifier, int):
            for d in devices:
                if d["id"] == identifier:
                    return identifier
                    
        target_str = str(identifier).lower()
        # Sanitize old WDM-KS strings from config
        target_str = target_str.replace("[windows wdm-ks]", "").replace("wdm-ks", "").strip()
        
        # 1. Exact full_label match
        for d in devices:
            if d["full_label"].lower() == target_str:
                return d["id"]
        # 2. Contains match (prioritizing WASAPI or DirectSound)
        for d in devices:
            if target_str in d["full_label"].lower() or target_str in d["name"].lower():
                return d["id"]
                
        # 3. Fallback to default output
        for d in devices:
            if d.get("is_default"):
                return d["id"]
                
        return None

    def auto_detect_devices(self) -> Tuple[Optional[int], Optional[int], Optional[int]]:
        """
        Auto-detects:
        - discord_out: Dedicated for Discord (e.g. Voicemeeter AUX Input, Sonar Chat, Voicemod)
        - all_mics_out: Broadcast mic (Voicemeeter Input, Sonar Mic, CABLE Input)
        - monitor_out: Default headphones
        Returns: (discord_out_id, all_mics_id, monitor_out_id)
        """
        outputs = self.list_output_devices()
        default_out = None
        discord_out = None
        all_mics_out = None
        
        for d in outputs:
            if d["is_default"]:
                default_out = d["id"]
                break
        if default_out is None and outputs:
            default_out = outputs[0]["id"]
            
        # 1. Look for Discord output: Dedicated CABLE Input first, then Voicemeeter Input (B1), Sonar Chat, etc.
        discord_keywords = [
            "sonar - microphone",
            "sonar - chat",
            "cable input",
            "voicemeeter input",
            "voicemeeter vaio3",
            "voicemod",
            "voicemeeter aux input"
        ]
        for kw in discord_keywords:
            for d in outputs:
                if kw in d["name"].lower():
                    discord_out = d["id"]
                    break
            if discord_out is not None:
                break

        # 2. Look for primary virtual mic
        all_mic_keywords = [
            "cable input",
            "voicemeeter input",
            "sonar - microphone"
        ]
        for kw in all_mic_keywords:
            for d in outputs:
                if kw in d["name"].lower():
                    all_mics_out = d["id"]
                    break
            if all_mics_out is not None:
                break

        if discord_out is None:
            discord_out = all_mics_out

        return discord_out, all_mics_out, default_out

    def get_effective_output_device_id(self) -> Optional[int]:
        """Resolves target output device ID based on active routing mode."""
        mode = config.get("routing_mode", "discord_only")
        
        if mode == "discord_only":
            setting = config.get("discord_output_device", "")
            dev_id = self.resolve_device_id(setting, is_output=True)
            if dev_id is not None:
                return dev_id
            # Fallback to auto-detect
            d_auto, _, _ = self.auto_detect_devices()
            return d_auto
            
        elif mode == "all_mics":
            setting = config.get("virtual_mic_device", "")
            dev_id = self.resolve_device_id(setting, is_output=True)
            if dev_id is not None:
                return dev_id
            _, a_auto, _ = self.auto_detect_devices()
            return a_auto
            
        else: # custom
            setting = config.get("virtual_mic_device", "")
            return self.resolve_device_id(setting, is_output=True)

    async def _synthesize_edge_tts(self, text: str, voice: str, rate: str, pitch: str) -> Tuple[np.ndarray, int]:
        communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate, pitch=pitch)
        audio_bytes = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_bytes += chunk["data"]
                
        if not audio_bytes:
            raise ValueError("No audio returned from edge-tts")
            
        f = io.BytesIO(audio_bytes)
        data, sr = sf.read(f, dtype="float32")
        return data, sr

    def _synthesize_pyttsx3(self, text: str) -> Tuple[np.ndarray, int]:
        engine = pyttsx3.init()
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tf:
            temp_path = tf.name
            
        try:
            engine.save_to_file(text, temp_path)
            engine.runAndWait()
            data, sr = sf.read(temp_path, dtype="float32")
            return data, sr
        finally:
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception:
                    pass

    def synthesize(self, text: str) -> Tuple[np.ndarray, int]:
        engine_type = config.get("tts_engine", "edge-tts")
        voice = config.get("voice", "en-US-ChristopherNeural")
        rate = config.get("rate", "+0%")
        pitch = config.get("pitch", "+0Hz")
        
        if engine_type == "edge-tts":
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                data, sr = loop.run_until_complete(self._synthesize_edge_tts(text, voice, rate, pitch))
                loop.close()
                return data, sr
            except Exception as e:
                print(f"[AudioEngine] edge-tts error: {e}. Falling back to pyttsx3.")
                
        return self._synthesize_pyttsx3(text)

    def speak(self, text: str, on_done: Optional[Callable[[], None]] = None):
        if not text or not text.strip():
            if on_done:
                on_done()
            return
            
        self.stop()
        
        def worker():
            self._is_speaking = True
            if self.on_state_change:
                self.on_state_change(True)
                
            try:
                audio_data, sr = self.synthesize(text)
                self._play_dual(audio_data, sr)
            except Exception as e:
                print(f"[AudioEngine] Speak failed: {e}")
                traceback.print_exc()
            finally:
                self._is_speaking = False
                if self.on_state_change:
                    self.on_state_change(False)
                if on_done:
                    on_done()
                    
        threading.Thread(target=worker, daemon=True).start()

    def _play_dual(self, audio_data: np.ndarray, orig_sr: int):
        self._stop_event.clear()
        
        if audio_data.ndim == 1:
            audio_data = np.column_stack((audio_data, audio_data))
            
        target_dev_id = self.get_effective_output_device_id()
        mon_dev_setting = config.get("monitor_device", "")
        play_monitor = config.get("play_monitor", True)
        
        mon_id = self.resolve_device_id(mon_dev_setting, is_output=True) if play_monitor else None
        
        if mon_id is None and play_monitor:
            _, _, m_auto = self.auto_detect_devices()
            mon_id = m_auto
            
        vol_mic = float(config.get("volume_mic", 1.0))
        vol_mon = float(config.get("volume_monitor", 0.8))
        
        playback_threads = []
        
        def play_to_device(dev_id: int, vol: float):
            try:
                dev_info = sd.query_devices(dev_id)
                native_sr = int(dev_info.get("default_samplerate", orig_sr))
                
                if native_sr != orig_sr:
                    scaled_audio = resample_audio(audio_data, orig_sr, native_sr) * vol
                    playback_sr = native_sr
                else:
                    scaled_audio = audio_data * vol
                    playback_sr = orig_sr
                    
                sd.play(scaled_audio, samplerate=playback_sr, device=dev_id, blocking=True)
            except Exception as e:
                print(f"[AudioEngine] Warning: Device {dev_id} playback issue: {e}")
                # Safe fallback to system default output
                default_dev = sd.default.device[1]
                if dev_id != default_dev and default_dev is not None:
                    try:
                        sd.play(audio_data * vol, samplerate=orig_sr, device=default_dev, blocking=True)
                    except Exception:
                        pass

        if target_dev_id is not None:
            t1 = threading.Thread(target=play_to_device, args=(target_dev_id, vol_mic), daemon=True)
            t1.start()
            playback_threads.append(t1)
            
        if mon_id is not None and mon_id != target_dev_id:
            t2 = threading.Thread(target=play_to_device, args=(mon_id, vol_mon), daemon=True)
            t2.start()
            playback_threads.append(t2)
            
        for t in playback_threads:
            t.join()

    def stop(self):
        self._stop_event.set()
        try:
            sd.stop()
        except Exception:
            pass
        self._is_speaking = False
        if self.on_state_change:
            self.on_state_change(False)

# Global engine instance
audio_engine = AudioEngine()
