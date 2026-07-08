import Foundation

/// The chuzhditsa keyboard layout: a Bulgarian phonetic base with every
/// extension letter reachable by long-press on its featural base key.
enum Layout {
    // Main Cyrillic page
    static let rows: [[String]] = [
        ["я", "в", "е", "р", "т", "ъ", "у", "и", "о", "п"],
        ["а", "с", "д", "ф", "г", "х", "й", "к", "л", "ш"],
        ["з", "ь", "ц", "ж", "б", "н", "м", "ч"],
    ]

    // Long-press alternates: base key -> extension letters (featural neighbors)
    static let alternates: [String: [String]] = [
        "а": ["ӓ", "а̨", "а̄", "а́", "а̀", "а̌"],
        "е": ["ѧ", "ѩ", "е̄", "ѐ", "є", "э"],
        "и": ["ӣ", "ѝ", "і", "ї", "ы"],
        "о": ["ӧ", "ѫ", "ѭ", "о̄", "ё"],
        "у": ["ў", "ӱ", "ӯ", "ю"],
        "ъ": ["ы", "ѫ"],
        "я": ["ѩ"],
        "в": ["ў"],
        "т": ["т̢", "тʰ", "тӀ", "ћ"],
        "д": ["д̢", "дʱ", "ђ", "ѕ"],
        "с": ["ҫ", "сь"],
        "з": ["ҙ", "ѕ"],
        "к": ["қ", "кʰ", "кӀ", "ќ"],
        "г": ["ғ", "гʱ", "ґ", "ѓ"],
        "х": ["ҳ", "һ", "хь"],
        "н": ["ң", "н̢", "нь"],
        "л": ["ль"],
        "ч": ["џ", "чʰ", "чӀ"],
        "ц": ["ѕ", "цӀ"],
        "ж": ["џ"],
        "р": ["р̢"],
        "п": ["пʰ", "пӀ"],
        "б": ["бʱ"],
        "й": ["ј"],
        "ь": ["ѩ", "ѭ"],
        "ш": ["щ"],
        "м": ["ѫ"],
    ]

    // Symbols/marks page
    static let symbolRows: [[String]] = [
        ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
        ["ʰ", "ʱ", "Ӏ", "\u{0304}", "\u{0301}", "\u{0300}", "\u{030C}", "\u{0328}", "\u{0322}"],
        ["–", "—", "·", "«", "»", "’", "!", "?"],
    ]

    static let symbolAlternates: [String: [String]] = [
        "’": ["'"],
        "–": ["-"],
    ]

    /// Display label for combining marks (rendered on a dotted circle)
    static func label(for key: String) -> String {
        if let scalar = key.unicodeScalars.first, key.unicodeScalars.count == 1,
           (0x0300...0x036F).contains(scalar.value) {
            return "\u{25CC}" + key
        }
        return key
    }
}
