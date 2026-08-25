# Receiver Adaptation

The receiver is the most hardware-specific part of the Intercom path.

## Current configuration knob

`INTERCOM_INPUT` controls the Zone 2 source. The known-good MAIN-zone selection is implemented in code for SAT/CATV. If your receiver requires a different MAIN input, adapt `MAIN_INPUT_FEATURES` and `prepare_intercom_route()` in `intercom/app.py`.

Reference Zone 2 value on the STR-ZA1100ES:

```text
sat
```

Known MAIN feature names present in the reference remote include `GUI.tv`, `GUI.bddvd`, `GUI.game`, `GUI.sat`, `GUI.video`, and `GUI.aux`. Do not assume your model supports all of them.

## Why MAIN and Zone 2 both matter

On the reference STR-ZA1100ES, setting only:

```text
zone2.input = sat
```

reported SAT correctly but did not physically route the NAS HDMI audio to the Zone 2 analog output. MAIN also had to be switched to SAT/CATV.

The backend therefore reads the current MAIN input, selects SAT/CATV, powers Zone 2, selects the Zone 2 source, plays audio, powers Zone 2 off, and restores the original MAIN input.

Your receiver may behave differently. Physically verify the output instead of trusting only the API response.

## Read the current MAIN input

PowerShell:

```powershell
$body = @{
    type = "http_get"
    packet = @(@{ id = 100; feature = "main.input" })
} | ConvertTo-Json -Depth 6

Invoke-WebRequest `
    -Uri "http://YOUR_RECEIVER_IP/request.cgi" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body |
    Select-Object -ExpandProperty Content
```

## Test a candidate MAIN feature

Only use a feature name you have verified for your receiver.

```powershell
$body = @{
    type = "http_set"
    packet = @(@{ id = 101; feature = "GUI.sat"; value = "main" })
} | ConvertTo-Json -Depth 6

Invoke-WebRequest `
    -Uri "http://YOUR_RECEIVER_IP/request.cgi" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body |
    Select-Object -ExpandProperty Content
```

Physically verify that the receiver display and audio route change. An HTTP success response alone is not enough.

## Test Zone 2 separately

Read and set `zone2.power` and `zone2.input` independently, then verify the physical output.

If you get another Sony receiver working, document its tested values and model-specific quirks.
