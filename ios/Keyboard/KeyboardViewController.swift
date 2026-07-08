import UIKit
import CoreText

/// The chuzhditsa custom keyboard: Bulgarian phonetic base layout with all
/// extension letters on long-press, keycaps set in the Chuzhditsa face.
final class KeyboardViewController: UIInputViewController {

    private var shifted = true
    private var symbolsPage = false
    private var keyboardStack: UIStackView?
    private var popup: PopupView?

    override func viewDidLoad() {
        super.viewDidLoad()
        registerBundledFont()
        rebuild()
    }

    // MARK: - Font

    private static var fontRegistered = false
    private func registerBundledFont() {
        guard !Self.fontRegistered,
              let url = Bundle(for: KeyboardViewController.self)
                .url(forResource: "Chuzhditsa-Regular", withExtension: "otf") else { return }
        CTFontManagerRegisterFontsForURL(url as CFURL, .process, nil)
        Self.fontRegistered = true
    }

    private func keyFont(_ size: CGFloat) -> UIFont {
        UIFont(name: "Chuzhditsa", size: size) ?? .systemFont(ofSize: size)
    }

    // MARK: - Layout construction

    private func rebuild() {
        keyboardStack?.removeFromSuperview()
        let rows = symbolsPage ? Layout.symbolRows : Layout.rows
        var rowViews: [UIView] = rows.enumerated().map { idx, row in
            makeRow(row, isLetterRow: !symbolsPage, isLastLetterRow: !symbolsPage && idx == rows.count - 1)
        }
        rowViews.append(makeBottomRow())

        let stack = UIStackView(arrangedSubviews: rowViews)
        stack.axis = .vertical
        stack.distribution = .fillEqually
        stack.spacing = 8
        stack.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(stack)
        NSLayoutConstraint.activate([
            stack.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 4),
            stack.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -4),
            stack.topAnchor.constraint(equalTo: view.topAnchor, constant: 8),
            stack.bottomAnchor.constraint(equalTo: view.bottomAnchor, constant: -8),
            stack.heightAnchor.constraint(greaterThanOrEqualToConstant: 200),
        ])
        keyboardStack = stack
    }

    private func makeRow(_ keys: [String], isLetterRow: Bool, isLastLetterRow: Bool) -> UIView {
        var views: [UIView] = keys.map { makeKey($0) }
        if isLastLetterRow {
            views.insert(makeControlKey("⇧", action: #selector(toggleShift)), at: 0)
            views.append(makeControlKey("⌫", action: #selector(backspace)))
        }
        let stack = UIStackView(arrangedSubviews: views)
        stack.axis = .horizontal
        stack.distribution = .fillProportionally
        stack.spacing = 5
        return stack
    }

    private func makeBottomRow() -> UIView {
        let mode = makeControlKey(symbolsPage ? "абв" : "123", action: #selector(toggleSymbols))
        let space = makeControlKey("интервал", action: #selector(insertSpace))
        space.setContentHuggingPriority(.defaultLow, for: .horizontal)
        let ret = makeControlKey("⏎", action: #selector(insertReturn))
        var views: [UIView] = [mode]
        if needsInputModeSwitchKey {
            let globe = makeControlKey("🌐", action: nil)
            globe.addTarget(self, action: #selector(handleInputModeList(from:with:)), for: .allTouchEvents)
            views.append(globe)
        }
        views.append(space)
        views.append(ret)
        let stack = UIStackView(arrangedSubviews: views)
        stack.axis = .horizontal
        stack.spacing = 5
        space.widthAnchor.constraint(greaterThanOrEqualTo: stack.widthAnchor, multiplier: 0.45).isActive = true
        return stack
    }

    private func makeKey(_ key: String) -> UIButton {
        let button = KeyButton(type: .system)
        button.key = key
        button.setTitle(displayed(Layout.label(for: key)), for: .normal)
        button.titleLabel?.font = keyFont(24)
        style(button)
        button.addTarget(self, action: #selector(keyTapped(_:)), for: .touchUpInside)
        if Layout.alternates[key] != nil || Layout.symbolAlternates[key] != nil {
            let press = UILongPressGestureRecognizer(target: self, action: #selector(keyLongPressed(_:)))
            press.minimumPressDuration = 0.35
            button.addGestureRecognizer(press)
        }
        return button
    }

    private func makeControlKey(_ label: String, action: Selector?) -> UIButton {
        let button = UIButton(type: .system)
        button.setTitle(label, for: .normal)
        button.titleLabel?.font = .systemFont(ofSize: 17, weight: .medium)
        style(button, control: true)
        if let action { button.addTarget(self, action: action, for: .touchUpInside) }
        return button
    }

    private func style(_ button: UIButton, control: Bool = false) {
        button.backgroundColor = control
            ? UIColor.secondarySystemFill
            : UIColor.systemBackground.withAlphaComponent(0.9)
        button.setTitleColor(.label, for: .normal)
        button.layer.cornerRadius = 6
        button.layer.shadowColor = UIColor.black.cgColor
        button.layer.shadowOpacity = 0.18
        button.layer.shadowOffset = CGSize(width: 0, height: 1)
        button.layer.shadowRadius = 0.5
    }

    private func displayed(_ key: String) -> String {
        shifted && !symbolsPage ? key.uppercased() : key
    }

    // MARK: - Actions

    @objc private func keyTapped(_ sender: KeyButton) {
        guard let key = sender.key else { return }
        textDocumentProxy.insertText(displayed(key))
        if shifted && !symbolsPage {
            shifted = false
            retitleAll()
        }
    }

    @objc private func keyLongPressed(_ gesture: UILongPressGestureRecognizer) {
        guard let button = gesture.view as? KeyButton, let key = button.key,
              let alts = Layout.alternates[key] ?? Layout.symbolAlternates[key] else { return }
        switch gesture.state {
        case .began:
            let items = alts.map { displayed($0) }
            let popup = PopupView(items: items, font: keyFont(26))
            view.addSubview(popup)
            popup.place(above: button, in: view)
            self.popup = popup
        case .changed:
            popup?.highlight(at: gesture.location(in: popup))
        case .ended:
            if let choice = popup?.selected { textDocumentProxy.insertText(choice) }
            fallthrough
        default:
            popup?.removeFromSuperview()
            popup = nil
        }
    }

    @objc private func toggleShift() { shifted.toggle(); retitleAll() }
    @objc private func toggleSymbols() { symbolsPage.toggle(); rebuild() }
    @objc private func insertSpace() { textDocumentProxy.insertText(" ") }
    @objc private func insertReturn() { textDocumentProxy.insertText("\n") }
    @objc private func backspace() { textDocumentProxy.deleteBackward() }

    private func retitleAll() {
        keyboardStack?.arrangedSubviews.forEach { row in
            (row as? UIStackView)?.arrangedSubviews.forEach { v in
                if let b = v as? KeyButton, let k = b.key {
                    b.setTitle(displayed(Layout.label(for: k)), for: .normal)
                }
            }
        }
    }
}

final class KeyButton: UIButton {
    var key: String?
}

/// Long-press alternates bubble with slide-to-select.
final class PopupView: UIView {
    private var labels: [UILabel] = []
    private(set) var selected: String?

    init(items: [String], font: UIFont) {
        super.init(frame: .zero)
        backgroundColor = .systemBackground
        layer.cornerRadius = 8
        layer.borderWidth = 0.5
        layer.borderColor = UIColor.separator.cgColor
        layer.shadowOpacity = 0.25
        layer.shadowRadius = 4
        let stack = UIStackView()
        stack.axis = .horizontal
        stack.distribution = .fillEqually
        stack.translatesAutoresizingMaskIntoConstraints = false
        for item in items {
            let label = UILabel()
            label.text = item
            label.font = font
            label.textAlignment = .center
            label.layer.cornerRadius = 6
            label.layer.masksToBounds = true
            labels.append(label)
            stack.addArrangedSubview(label)
        }
        addSubview(stack)
        NSLayoutConstraint.activate([
            stack.leadingAnchor.constraint(equalTo: leadingAnchor, constant: 6),
            stack.trailingAnchor.constraint(equalTo: trailingAnchor, constant: -6),
            stack.topAnchor.constraint(equalTo: topAnchor, constant: 4),
            stack.bottomAnchor.constraint(equalTo: bottomAnchor, constant: -4),
        ])
        selected = items.first
        highlightIndex(0)
    }

    required init?(coder: NSCoder) { fatalError() }

    func place(above key: UIView, in container: UIView) {
        let keyFrame = key.convert(key.bounds, to: container)
        let width = CGFloat(labels.count) * max(44, keyFrame.width) + 12
        let x = min(max(4, keyFrame.midX - width/2), container.bounds.width - width - 4)
        frame = CGRect(x: x, y: keyFrame.minY - 58, width: width, height: 52)
    }

    func highlight(at point: CGPoint) {
        let inner = CGFloat(6)
        let cell = (bounds.width - inner*2) / CGFloat(max(labels.count, 1))
        let idx = max(0, min(labels.count - 1, Int((point.x - inner) / cell)))
        highlightIndex(idx)
    }

    private func highlightIndex(_ idx: Int) {
        for (i, label) in labels.enumerated() {
            label.backgroundColor = i == idx ? .systemBlue.withAlphaComponent(0.25) : .clear
        }
        selected = labels.indices.contains(idx) ? labels[idx].text : selected
    }
}
