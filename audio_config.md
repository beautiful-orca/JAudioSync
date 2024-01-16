### Audio Setup
- Test sounds: `speaker-test -c 1`
- `alsamixer` (interactive shell), identify audio cards

#### Default sound card config with Stereo
`~/.asoundrc`
```
pcm.!default {
   type hw
   card 0
}

ctl.!default {
   type hw
   card 0
}
```

#### USB DAC Digital Audio sound card
- Find USB-AUDIO device: `aplay -l`
```
**** List of PLAYBACK Hardware Devices ****
card 0: Headphones [bcm2835 Headphones], device 0: bcm2835 Headphones [bcm2835 Headphones]
card 1: Audio [KM_B2 Digital Audio], device 0: USB Audio [USB Audio]
card 2: vc4hdmi [vc4-hdmi], device 0: MAI PCM i2s-hifi-0 [MAI PCM i2s-hifi-0]
```

#### Disable onboard analog audio
- Avoid conflicts for default device when using USB Audio
`echo "blacklist snd_bcm2835" | sudo tee /etc/modprobe.d/alsa-blacklist.conf > /dev/null`

#### Two Mono Channels with "Audio"
`~/.asoundrc`
```
pcm.!default {
    type plug
    slave.pcm "mono"
}

pcm.mono {
    type route
    slave.pcm "hw:Audio"
    ttable.0.0 0.5  # Left channel to left output
    ttable.1.0 0.5  # Right channel to left output
    ttable.0.1 0.5  # Left channel to right output
    ttable.1.1 0.5  # Right channel to right output
}

ctl.mono {
    type hw
    card Audio
}
```
