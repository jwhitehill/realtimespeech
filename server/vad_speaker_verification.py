# vad_speaker_verification.py receives the audio tensor from ser_audio_process.py and does voice activity detection and proceed to speechbrain speaker verification 
import torch
import speechbrain
import torchaudio
import os
import numpy as np
from speechbrain.pretrained import SpeakerRecognition
import webrtcvad

verification = SpeakerRecognition.from_hparams(source="speechbrain/spkrec-ecapa-voxceleb", savedir="pretrained_models/spkrec-ecapa-voxceleb")
sample_list = {}
sr = 16000
similarity = torch.nn.CosineSimilarity(dim=-1, eps=1e-6)

vad = webrtcvad.Vad()
vad.set_mode(3)
frame_duration = 960  # ms

def load_samples():
    '''load all sample audio into a list of tensors for later comparison
    
    Returns:
        sample_list: a dictionary with speaker name as the key and sample audio embedding as value

    '''
    global sample_list
    sample_dir = './speaker_voice_sample/'
    # list all samples in directory
    sample_path_list = os.listdir(sample_dir)
    for sample_path in sample_path_list:
        # load each individual numpy array and convert to tensor
        sample_audio = np.load(sample_dir + sample_path, allow_pickle=True)
        sample_audio_tensor = torch.from_numpy(sample_audio)
        sample_audio_flat = sample_audio_tensor.flatten()
        # create and store the embedding of the speaker voice sample
        sample_audio_emb = verification.encode_batch(sample_audio_flat, wav_lens=None, normalize=True)
        # get the name of the speaker
        sample_name = sample_path.split('.')[0]
        sample_list[sample_name] = sample_audio_emb
    return sample_list

def float_to_pcm16(audio):
    '''conver data from float to pcm16, supported by WebRTC-VAD.
    
    Args:
        audio: 1-second numpy array audio in float64 dypte

    Returns:
        buf: audio converted to int16, then to bytes
        
    '''
    ints = (audio * 32768).astype(np.int16)
    little_endian = ints.astype('<u2')
    buf = little_endian.tobytes()
    return buf

def vad_impl(audio_data):
    '''Implementation of webrtvad, can be used on float64 dtype array
    
    Args:
        audio_data: 1-second numpy array audio data

    Retuns:
        contains_speech: boolean for whether the audio is a speech

    '''
    audio_data_pcm16 = float_to_pcm16(audio_data)
    contains_speech = False
    # Process the audio in frames and check for speech
    for i in range(0, len(audio_data_pcm16), frame_duration):
        frame = audio_data_pcm16[i:i+frame_duration]
        if len(frame) < frame_duration:
            # Pad the last frame with zeros if needed
            frame = np.pad(frame, (0, frame_duration - len(frame)))
        if vad.is_speech(frame, sr):
            contains_speech = True
            break  # Exit the loop if speech is detected
    return contains_speech

def compare_recording(audio_tensor):
    '''compare the recordings and return the speaker with the max score
    
    Args:
        audio_tensor: audio tensor got from server_audio_process.py for audio processing

    Returns:
        max_key: string of the name of the most closely-matched speaker

    '''
    rt_audio_np = audio_tensor.numpy()
    # a simple vad system, may uncomment the line below for webrtvad
    contains_speech = rt_audio_np.std() > 1e-3
    #contains_speech = vad_impl(rt_audio_np)
    if contains_speech == False:
        return "Not Speech"
    # flatten the incoming audio tensor and create embedding
    rt_audio_tensor_flat = audio_tensor.flatten()
    rt_audio_emb = verification.encode_batch(rt_audio_tensor_flat, wav_lens=None, normalize=True)
    # scores for each comparison
    scores = {}
    for sample_name, sample_audio_emb in sample_list.items():
        # get the score for speaker verification and put it in pair with the speaker sample name
        scores[sample_name] = similarity(rt_audio_emb, sample_audio_emb)
    # Find the maximum value in the dictionary
    print("comparison scores:")
    print(scores.values())
    max_value = max(scores.values())

    # Find the key corresponding to the maximum value
    max_key = [key for key, value in scores.items() if value == max_value][0]
    return max_key

def main():
    load_samples()

if __name__ == "__main__":
    main()

