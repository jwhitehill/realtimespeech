import torch
import speechbrain
import torchaudio
import os
import numpy as np
from speechbrain.pretrained import SpeakerRecognition

verification = SpeakerRecognition.from_hparams(source="speechbrain/spkrec-ecapa-voxceleb", savedir="pretrained_models/spkrec-ecapa-voxceleb")
sample_list = {}
sr = 16000
similarity = torch.nn.CosineSimilarity(dim=-1, eps=1e-6)

# load all sample audio into a list of tensors for later comparison
def load_samples():
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

# compare the recordings and return the speaker with the max score
def compare_recording(audio_tensor):
    # flatten the incoming audio tensor and create embedding
    rt_audio_tensor_flat = audio_tensor.flatten()
    rt_audio_emb = verification.encode_batch(rt_audio_tensor_flat, wav_lens=None, normalize=True)
    # scores for each comparison
    scores = {}
    for sample_name, sample_audio_emb in sample_list.items():
        # get the score for speaker verification and put it in pair with the speaker sample name
        #print("real-time tensor:")
        #print(audio_tensor_unsqueeze)
        #print("sample tensor:")
        #print(sample_audio)
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

