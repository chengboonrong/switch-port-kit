import SwiftUI

@main
struct ProbeApp: App {
    var body: some Scene {
        WindowGroup { ProbeView() }
    }
}

struct ProbeView: View {
    @State private var result = "Tap Run Probe to inspect the local Metal device."
    @State private var running = false

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 16) {
                    Text("SwitchPortKit · Hardware Research")
                        .font(.headline)
                        .accessibilityIdentifier("probe.heading")
                    Text("Reports Metal capabilities. This does not run Nintendo Switch games.")
                        .foregroundStyle(.secondary)
                    Button(running ? "Running…" : "Run Probe") {
                        guard !running else { return }
                        running = true
                        result = "Running diagnostics…"
                        Task {
                            let report = await Task.detached(priority: .userInitiated) {
                                MetalProbe.run()
                            }.value
                            result = report
                            running = false
                        }
                    }
                    .disabled(running)
                    .buttonStyle(.borderedProminent)
                    .accessibilityIdentifier("probe.run")
                    ShareLink(item: result) {
                        Label("Share Diagnostics", systemImage: "square.and.arrow.up")
                    }
                    .disabled(running)
                    .accessibilityIdentifier("probe.share")
                    Text(result)
                        .font(.system(.footnote, design: .monospaced))
                        .textSelection(.enabled)
                        .accessibilityIdentifier("probe.report")
                }
                .padding()
            }
            .navigationTitle("A17 Pro Metal Probe")
        }
    }
}
