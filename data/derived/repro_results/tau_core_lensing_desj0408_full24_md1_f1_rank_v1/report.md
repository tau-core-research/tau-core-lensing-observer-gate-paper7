# DES J0408 Full-24 MD1/F1 Rank Audit v1

**Verdict:** `DESJ0408_DELAY_ONLY_STRUCTURAL_F1_NO_GO_WITH_PRACTICAL_WEAK_DIRECTION`

The nuisance basis was frozen from all 24 public no-T2 model predictions before the observed delay vector was projected.

| quantity | result |
| --- | ---: |
| raw path-output dimension | 2 |
| empirical nuisance rank | 2 |
| covariance-whitened nuisance rank | 2 |
| remaining delay-only F1 dimension | 0 |
| leave-one-model-out rank-2 fraction | 1.000 |
| bootstrap rank-2 fraction at 5% tolerance | 1.000 |

The exact result is a structural measurement-design no-go. Covariance whitening exposes a weak second nuisance direction, so a thresholded practical sensitivity direction is retained separately as a follow-up target, not a detection.

## Rank Repair

Add a genuinely third path-sensitive observable, or independently constrain the lens/source nuisance family until its effective rank is below two. Freeze the repaired design before inspecting any Tau endpoint score.
