import SwiftUI

@main
struct ChuzhditsaApp: App {
    var body: some Scene {
        WindowGroup { SetupView() }
    }
}

struct SetupView: View {
    var body: some View {
        NavigationStack {
            List {
                Section {
                    Text("Чуждица е клавиатура за чужди думи: разширена кирилица с букви за звуковете, които стандартната азбука няма — ў, ҫ, ҙ, ӓ, ң, қ, ҳ, һ, юсовете и още.")
                    Text("Chuzhditsa is a keyboard for foreign words: extended Cyrillic with letters for the sounds the standard alphabet lacks.")
                        .foregroundStyle(.secondary)
                }
                Section("Включване · Setup") {
                    Label("Отворете Settings → General → Keyboard", systemImage: "1.circle")
                    Label("Keyboards → Add New Keyboard…", systemImage: "2.circle")
                    Label("Изберете „Чуждица“", systemImage: "3.circle")
                    Label("Задръжте 🌐 в кое да е поле, за да я изберете", systemImage: "4.circle")
                }
                Section("Как се пише · How to type") {
                    Text("Задръжте буква, за да видите разширенията ѝ: **у** дава ў ӱ ӯ ю; **с** дава ҫ; **т** дава т̢ тʰ тӀ. Страницата „123“ носи знаците за тон, дължина и придих.")
                    Text("Long-press a letter for its extensions; the 123 page carries the tone, length and aspiration marks.")
                        .foregroundStyle(.secondary)
                }
                Section {
                    Link("Спецификация · github.com/anastasds/chuzbitza",
                         destination: URL(string: "https://github.com/anastasds/chuzbitza")!)
                }
            }
            .navigationTitle("Чуждица")
        }
    }
}
