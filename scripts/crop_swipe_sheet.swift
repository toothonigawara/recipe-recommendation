import AppKit
import Foundation

let arguments = CommandLine.arguments
guard arguments.count >= 3 else {
    fputs("usage: crop_swipe_sheet.swift <source.png> <output-dir>\n", stderr)
    exit(1)
}

let sourcePath = arguments[1]
let outputDir = URL(fileURLWithPath: arguments[2], isDirectory: true)
let names = [
    "omelette_rice", "ramen", "oyakodon", "ginger_pork", "yakisoba", "seafood_pasta", "curry_rice",
    "salted_salmon", "bibimbap", "kimchi_jjigae", "hiyayakko", "cold_soba", "egg_sandwich", "hamburger",
    "mapo_tofu", "fried_rice", "kaisendon", "green_salad", "caprese", "gratin", "tonkatsu",
    "sanma_shioyaki", "niku_udon", "kimbap", "pizza_toast", "minestrone", "tuna_mayo_onigiri", "nikujaga"
]

guard let image = NSImage(contentsOfFile: sourcePath),
      let source = image.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
    fputs("failed to read source image\n", stderr)
    exit(1)
}

let columns = 7
let cellWidth = source.width / columns
let cellHeight = source.height / 4
let fileManager = FileManager.default
try fileManager.createDirectory(at: outputDir, withIntermediateDirectories: true)

for (index, name) in names.enumerated() {
    let column = index % columns
    let row = index / columns
    let rect = CGRect(
        x: column * cellWidth,
        y: row * cellHeight,
        width: cellWidth,
        height: cellHeight
    )

    guard let cropped = source.cropping(to: rect) else {
        fputs("failed to crop \(name)\n", stderr)
        exit(1)
    }

    let bitmap = NSBitmapImageRep(cgImage: cropped)
    guard let data = bitmap.representation(using: .png, properties: [:]) else {
        fputs("failed to encode \(name)\n", stderr)
        exit(1)
    }

    let outURL = outputDir.appendingPathComponent("\(name).png")
    try data.write(to: outURL)
}

print("cropped \(names.count) images to \(outputDir.path)")
