from app.schemas import Language

TEXT = {
    "en": {
        "summary.lower_risk": "No strong warning signs were found in the checks that completed.",
        "summary.unclear": "Some checks were unavailable or the available evidence is inconclusive.",
        "summary.high_risk": "Multiple warning signs indicate a high-risk transaction.",
        "advice.default": "Verify the seller independently and use a payment method with buyer protection.",
        "advice.high_risk": "Do not pay until every warning sign has been independently resolved.",
        "advice.payment": "Confirm that the payment account belongs to the seller before sending money.",
        "advice.pressure": "Pause the transaction; urgency is not a reason to skip verification.",
        "limitation": "TrustCheck estimates risk from available signals; it does not certify that a seller is genuine or fraudulent.",
    },
    "hi": {
        "summary.lower_risk": "पूरी हुई जाँचों में कोई बड़ा चेतावनी संकेत नहीं मिला।",
        "summary.unclear": "कुछ जाँच उपलब्ध नहीं थीं या उपलब्ध प्रमाण निर्णायक नहीं हैं।",
        "summary.high_risk": "कई चेतावनी संकेत इस लेन-देन को अधिक जोखिम वाला बताते हैं।",
        "advice.default": "विक्रेता की स्वतंत्र रूप से पुष्टि करें और खरीदार सुरक्षा वाली भुगतान विधि चुनें।",
        "advice.high_risk": "हर चेतावनी संकेत की स्वतंत्र पुष्टि होने तक भुगतान न करें।",
        "advice.payment": "पैसे भेजने से पहले पुष्टि करें कि भुगतान खाता विक्रेता का ही है।",
        "advice.pressure": "लेन-देन रोकें; जल्दबाज़ी सत्यापन छोड़ने का कारण नहीं है।",
        "limitation": "TrustCheck उपलब्ध संकेतों से जोखिम का अनुमान लगाता है; यह किसी विक्रेता को असली या धोखेबाज़ प्रमाणित नहीं करता।",
    },
}


def text(language: Language, key: str) -> str:
    return TEXT[language][key]


def choose(language: Language, english: str, hindi: str) -> str:
    return hindi if language == "hi" else english