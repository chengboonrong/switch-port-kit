import type { E2EConfig } from 'e2e';
import { mobile } from '@e2e-dev/mobile';

export default {
  targets: [{
    name: 'ios',
    engine: mobile({ platform: 'ios' }),
    app: { bundleId: 'dev.switchportkit.A17ProMetalProbe' },
  }],
  workers: 1,
} satisfies E2EConfig;
