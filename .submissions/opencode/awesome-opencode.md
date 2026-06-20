# awesome-opencode/awesome-opencode

- Upstream: <https://github.com/awesome-opencode/awesome-opencode>
- Fork: <https://github.com/Goldziher/awesome-opencode>
- Branch: `add-kreuzberg-opencode-plugins`
- PR: <https://github.com/awesome-opencode/awesome-opencode/pull/420>
- Submitted: 2026-06-10
- Status: open
- Packages:
  - `@kreuzberg/opencode-kreuzberg@0.1.0`
  - `@kreuzberg/opencode-kreuzcrawl@0.1.0`
- Local validation: `npm pack --dry-run --workspace ...` passed for both packages.
- Publish status: npm publish succeeded on 2026-06-10; `npm dist-tag ls` shows `latest: 0.1.0` for both packages and `npm access get status` reports both public.
- Public metadata: `npm view` resolves both packages at `0.1.0`.
- Upstream validation: `npm ci` and `npm run validate -- data/plugins/kreuzberg.yaml data/plugins/kreuzcrawl.yaml` passed locally. `npm ci` reported existing upstream dependency audit findings.

## Next step

Track PR review.
