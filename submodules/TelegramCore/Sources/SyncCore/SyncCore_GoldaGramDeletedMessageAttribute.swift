import Foundation
import Postbox

/// Marks a message that the server deleted after the user had already received it.
/// GoldaGram keeps the local copy in its original position so the chat can render it as deleted.
public final class GoldaGramDeletedMessageAttribute: MessageAttribute {
    public let date: Int32

    public init(date: Int32) {
        self.date = date
    }

    required public init(decoder: PostboxDecoder) {
        self.date = decoder.decodeInt32ForKey("d", orElse: 0)
    }

    public func encode(_ encoder: PostboxEncoder) {
        encoder.encodeInt32(self.date, forKey: "d")
    }
}

public extension Message {
    var goldaGramDeletedDate: Int32? {
        return self.attributes.compactMap { ($0 as? GoldaGramDeletedMessageAttribute)?.date }.first
    }
}
