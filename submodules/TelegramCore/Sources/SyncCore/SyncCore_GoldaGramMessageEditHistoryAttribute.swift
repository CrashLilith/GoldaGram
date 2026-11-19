import Foundation
import Postbox

public final class GoldaGramMessageEditVersion: PostboxCoding {
    public let date: Int32
    public let text: String
    public let mediaSummary: String

    public init(date: Int32, text: String, mediaSummary: String) {
        self.date = date
        self.text = text
        self.mediaSummary = mediaSummary
    }

    public init(decoder: PostboxDecoder) {
        self.date = decoder.decodeInt32ForKey("d", orElse: 0)
        self.text = decoder.decodeStringForKey("t", orElse: "")
        self.mediaSummary = decoder.decodeStringForKey("m", orElse: "")
    }

    public func encode(_ encoder: PostboxEncoder) {
        encoder.encodeInt32(self.date, forKey: "d")
        encoder.encodeString(self.text, forKey: "t")
        encoder.encodeString(self.mediaSummary, forKey: "m")
    }
}

public final class GoldaGramMessageEditHistoryAttribute: MessageAttribute {
    public let versions: [GoldaGramMessageEditVersion]
    public let isRedacted: Bool

    public init(versions: [GoldaGramMessageEditVersion], isRedacted: Bool) {
        self.versions = versions
        self.isRedacted = isRedacted
    }

    required public init(decoder: PostboxDecoder) {
        self.versions = decoder.decodeObjectArrayForKey("v")
        self.isRedacted = decoder.decodeInt32ForKey("r", orElse: 0) != 0
    }

    public func encode(_ encoder: PostboxEncoder) {
        encoder.encodeObjectArray(self.versions, forKey: "v")
        encoder.encodeInt32(self.isRedacted ? 1 : 0, forKey: "r")
    }
}

public extension Message {
    var goldaGramEditHistory: GoldaGramMessageEditHistoryAttribute? {
        return self.attributes.first(where: { $0 is GoldaGramMessageEditHistoryAttribute }) as? GoldaGramMessageEditHistoryAttribute
    }

    var goldaGramIsRedacted: Bool {
        return self.goldaGramEditHistory?.isRedacted ?? false
    }
}

public extension EngineMessage {
    var goldaGramEditHistory: GoldaGramMessageEditHistoryAttribute? {
        return self._asMessage().goldaGramEditHistory
    }

    var goldaGramIsRedacted: Bool {
        return self._asMessage().goldaGramIsRedacted
    }
}
