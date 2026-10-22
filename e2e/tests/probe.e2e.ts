import { test } from '@e2e-dev/mobile';
import { expect } from 'e2e';

test('opens the diagnostics screen', async ({ app, screen }) => {
  await app.open();
  await expect(screen.getByTestId('probe.run')).toBeVisible();
  await expect(screen.getByTestId('probe.report')).toBeVisible();
});

test('runs the probe and displays a report', async ({ app, screen }) => {
  await app.open();
  await screen.getByTestId('probe.run').tap();
  // Simulator GPU capabilities are NOT evidence of iPad mini A17 Pro compatibility.
  await expect(screen.getByTestId('probe.report')).toContainText('host_contract_ping: PASS');
  await expect(screen.getByTestId('probe.report')).toContainText('host_contract_unknown_request: PASS');
  await expect(screen.getByTestId('probe.report')).toContainText('host_contract_monotonic_clock: PASS');
  await expect(screen.getByTestId('probe.report')).toContainText('host_contract_reserved_argument: PASS');
  await expect(screen.getByTestId('probe.report')).toContainText('guest_startup_config: PASS');
  await expect(screen.getByTestId('probe.report')).toContainText('hardware_probes: SKIPPED');
  await expect(screen.getByTestId('probe.share')).toBeVisible();
});
