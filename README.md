# Recorder
Recorder neuron for Kalliope

## Synopsis
Simple wave recorder for Kalliopes mircophone

## Installation
```bash
kalliope install --git-url https://github.com/corus87/recorder-neuron
```

## Options

| Parameter   | Required | Default        | Choices             | Comment                                                                |
|------------|----------|-------------|-----------------|-------------------------------------------------------|
| seconds     | yes        | None           | integer              | Not required if you only want to playback a file              |
| playback    | no          | False          | True/False         |                                                                              |
| file_name   | no          | default.wav |                        | If no file_name , record and playback will use default.wav |
| rate          | no          | 44100         | integer             |                                                                               |
| chunk        | no         | 1024           | integer              |                                                                              |
| format       | no         | paInt32       | paInt16, paInt24 |                                                                              |
| channels    | no         | 2                | integer              |                                                                              |


## Synapses example
```
  - name: "record-and-play"
    signals:
       - order: "record and play for {{ seconds }}"
    neurons:
      - recorder:
          seconds: {{ seconds }}
          file_name: new.wav
          playback: True        
          
  - name: "record-seconds"
    signals:
       - order: "start a {{ seconds }} second record"
    neurons:
      - say:
          message: "Starting a {{ seconds }} second record"
      - record:
          seconds: "{{ seconds }}"
      - say:
          message: "Record finished, starting playback"
      - recorder:
          playback: True

  - name: "play-record"
    signals:
       - order: "play record"
    neurons:
      - recorder:
          playback: True
          
```




