# Problems Log

## 2026-03-05

1. Android build blocked in this environment due missing local Android SDK configuration (`ANDROID_HOME` or `android/local.properties`).
   - Suggested remediation: install Android SDK commandline tools and set `sdk.dir` in `android/local.properties`.
2. Web scaffold currently uses `next@15.0.0` which reports a known critical vulnerability in npm audit output.
   - Suggested remediation: upgrade to patched Next.js version before production release.
