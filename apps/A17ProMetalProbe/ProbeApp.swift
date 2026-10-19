import SwiftUI

@main
struct ProbeApp: App {
    var body: some Scene {
        WindowGroup {
            ProbeView()
        }
    }
}

struct ProbeView: View {
    @State private var result = "Tap Run Probe to inspect the local Metal device."
    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 16) {
                    Text("SwitchPortKit · Hardware Research")
                        .font(.headline)
                    Text("Reports Metal capabilities. This does not run Nintendo Switch games.")
                        .foregroundStyle(.secondary)
                    Button("Run Probe") {
                        result = MetalProbe.run()
                    }
                    .buttonStyle(.borderedProminent)
                    ShareLink(item: result) {
                        Label("Share Diagnostics", systemImage: "square.and.arrow.up")
                    }
                    Text(result)
                        .font(.system(.footnote, design: .monospaced))
                        .textSelection(.enabled)
                }
                .padding()
            }
            .navigationTitle("A17 Pro Metal Probe")
        }
    }
}
