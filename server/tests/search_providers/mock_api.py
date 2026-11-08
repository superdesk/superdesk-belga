"""
Mock API Server for Belga Search Providers (Quart)
Reverse-engineered from search_providers.py & belga_newsml_mixin.py.
"""

from quart import Quart, jsonify, request

app = Quart(__name__)

# ==============================================================================
# MOCK DATA STORE
# ==============================================================================

MOCK_IMAGES = [
    {
        "imageId": 143831778,
        "userId": "MEFYJJ",
        "width": 4300,
        "height": 2868,
        "createDate": "2019-01-08T13:32:06Z",
        "name": "Signature of partnership agreement in Brussels",
        "caption": "Brussels, 08 January 2019: Official signing ceremony of the strategic partnership.",
        "author": "John Doe",
        "credit": "BELGA",
        "source": "BELGA",
        "smallUrl": "https://p.cdn.belga.be/belgaimage:143831778:600x140",
        "previewUrl": "https://3.t.cdn.belga.be/belgaimage:143831778:800x800",
        "thumbnailUrl": "https://3.t.cdn.belga.be/belgaimage:143831778:thumbnail",
        "detailUrl": "https://3.t.cdn.belga.be/belgaimage:143831778:1800x650",
    },
    {
        # Video item (Belga Image v2 format)
        "imageId": 143831779,
        "ID": 143831779,
        "userId": "MEFYJK",
        "width": 1920,
        "height": 1080,
        "createDate": "2019-01-08T14:15:00Z",
        "name": "Press conference highlights on climate policy",
        "caption": "Highlights of the press conference regarding new environmental regulations.",
        "author": "Jane Smith",
        "credit": "BELGA",
        "source": "BELGA",
        "smallUrl": "https://3.t.cdn.belga.be/belgaimage:143831779:thumb.jpg",
        "thumbnailUrl": "https://3.t.cdn.belga.be/belgaimage:143831779:thumb.jpg",
        "ThumbnailURL": "https://3.t.cdn.belga.be/belgaimage:143831779:thumb.jpg",
        "previewUrl": "https://3.t.cdn.belga.be/belgaimage:143831779:preview.jpg",
        "PreviewURL": "https://3.t.cdn.belga.be/belgaimage:143831779:preview.jpg",
        "videoPreviewUrl": "https://video.cdn.belga.be/media/143831779/preview.mp4",
        "VideoURL": "https://video.cdn.belga.be/media/143831779/original.mp4",
        "detailUrl": "https://video.cdn.belga.be/media/143831779/preview.mp4",
    },
]

MOCK_GALLERIES = [
    {
        "galleryId": "G987654",
        "name": "European Summit Coverage",
        "description": "Photo coverage of the EU leaders summit in Brussels.",
        "createDate": "2019-01-08T10:00:00Z",
        "author": "Belga Photo Desk",
        "userId": "BELGAPIC",
        "credit": "BELGA",
        "iconThumbnailUrl": "https://cdn.belga.be/gallery:G987654:thumb.jpg",
    }
]

MOCK_360_ARCHIVE_OBJECTS = [
    {
        "newsObjectId": 1001,
        "newsItemId": 5001,
        "assetType": "Text",
        "headLine": "Parliament approves new energy bill",
        "topic": "Politics",
        "name": "energy_bill_vote",
        "description": "Federal parliament passes revised energy framework.",
        "createDate": 1546954326000,
        "validateDate": 1546954330000,
        "credit": "BELGA",
        "source": "BELGA",
        "language": "FR",
        "city": "Brussels",
        "editorialInfo": "EMBARGO 18:00 CET",
        "keywords": ["ENERGY", "POLITICS", "BELGIUM"],
        "country": "belgium",
        "authors": [
            {"name": "Jean Dupont", "type": "reporter"},
            {"name": "Marie Curie", "type": "editor"},
        ],
        "packages": [{"newsService": "BELGA", "newsProduct": "GENERAL"}],
        "newsComponents": [
            {
                "assetType": "lead",
                "proxies": [
                    {
                        "varcharData": "The federal parliament on Tuesday approved the new energy bill."
                    }
                ],
            },
            {
                "assetType": "body",
                "proxies": [
                    {
                        "varcharData": "After several hours of debate, lawmakers voted in favor of the legislation.\nNew subsidies for green energy will take effect next quarter."
                    }
                ],
            },
        ],
    }
]

MOCK_360_ARCHIVE_ITEMS = {
    5001: [
        MOCK_360_ARCHIVE_OBJECTS[0],
        {
            "newsObjectId": 1002,
            "assetType": "RelatedArticle",
            "headLine": "Background on the energy transition debate",
            "topic": "Economy",
            "name": "energy_background",
            "description": "Historical overview of parliamentary discussions.",
            "createDate": 1546950000000,
            "validateDate": 1546950000000,
            "comments": "20190108120000",
            "credit": "BELGA",
            "source": "BELGA",
            "language": "FR",
            "authors": [],
            "newsComponents": [
                {
                    "assetType": "lead",
                    "proxies": [{"varcharData": "Analysis of the key provisions."}],
                },
                {
                    "assetType": "body",
                    "proxies": [
                        {
                            "varcharData": "Detailed background information on the reform."
                        }
                    ],
                },
            ],
        },
        {
            "newsObjectId": 1003,
            "assetType": "Picture",
            "headLine": "Parliament vote session",
            "topic": "Politics",
            "name": "parliament_vote_photo",
            "description": "Chamber of representatives during the vote.",
            "createDate": 1546954326000,
            "credit": "BELGA",
            "source": "BELGA",
            "language": "FR",
            "renderUrls": {
                "highres": "https://cdn.belga.be/360/1003/high.jpg",
                "preview": "https://cdn.belga.be/360/1003/prev.jpg",
                "thumbnail": "https://cdn.belga.be/360/1003/thumb.jpg",
            },
            "newsComponents": [
                {
                    "assetType": "Image",
                    "proxies": [],
                },
                {
                    "assetType": "Caption",
                    "proxies": [
                        {"varcharData": "Lawmakers cast their votes electronically."}
                    ],
                },
            ],
        },
    ]
}

MOCK_BELGA_PRESS = [
    {
        "uuid": "550e8400-e29b-41d4-a716-446655440000",
        "title": "Nieuwe maatregelen voor openbaar vervoer",
        "lead": "Vanaf volgende maand gelden aangepaste dienstregelingen voor trein en bus.",
        "body": "<p>De openbaarvervoermaatschappijen hebben vandaag hun nieuwe plannen voorgesteld.</p><p>Er komen extra verbindingen tijdens de spitsuren.</p>",
        "publishDate": "2021-05-18T10:30:00Z",
        "source": "De Standaard",
        "language": "NL",
        "wordCount": 350,
    }
]


# ==============================================================================
# AUTHENTICATION ENDPOINTS (NO-OP / PASSTHROUGH)
# ==============================================================================


@app.route("/authorizeUser", methods=["GET"])
@app.route("/belgaimage-api/authorizeUser", methods=["GET"])
async def authorize_user():
    """Belga Image v1 auth endpoint."""
    return jsonify(
        {
            "idToken": "mock-belga-id-token",
            "authToken": "mock-belga-auth-token",
        }
    )


@app.route("/auth/realms/belga/protocol/openid-connect/token", methods=["POST"])
@app.route("/openid-connect/token", methods=["POST"])
async def openid_token():
    """Belga Press OpenID Connect token endpoint."""
    return jsonify(
        {
            "access_token": "mock-belga-press-access-token",
            "token_type": "Bearer",
            "expires_in": 3600,
        }
    )


# ==============================================================================
# BELGA IMAGE / IMAGE V2 ENDPOINTS
# ==============================================================================


@app.route("/searchImages", methods=["GET"])
@app.route("/belgaimage-api/searchImages", methods=["GET"])
async def search_images():
    """Endpoint for BelgaImageSearchProvider & BelgaImageV2SearchProvider find_async."""
    offset = int(request.args.get("s", 0))
    limit = int(request.args.get("l", 25))

    paged_items = MOCK_IMAGES[offset : offset + limit]
    return jsonify(
        {
            "nrImages": len(MOCK_IMAGES),
            "images": paged_items,
        }
    )


@app.route("/getImageById", methods=["GET"])
@app.route("/belgaimage-api/getImageById", methods=["GET"])
async def get_image_by_id():
    """Endpoint for BelgaImageSearchProvider & BelgaImageV2SearchProvider fetch_async."""
    image_id_str = str(request.args.get("i", "")).rsplit(":", 1)[-1]
    for item in MOCK_IMAGES:
        if (
            str(item.get("imageId")) == image_id_str
            or str(item.get("ID")) == image_id_str
        ):
            return jsonify(item)
    # Fallback to first image item
    return jsonify(MOCK_IMAGES[0])


# ==============================================================================
# BELGA COVERAGE / COVERAGE V2 ENDPOINTS
# ==============================================================================


@app.route("/searchGalleries", methods=["GET"])
@app.route("/belgaimage-api/searchGalleries", methods=["GET"])
async def search_galleries():
    """Endpoint for BelgaCoverageSearchProvider & BelgaCoverageV2SearchProvider find_async."""
    offset = int(request.args.get("s", 0))
    limit = int(request.args.get("l", 25))

    paged_items = MOCK_GALLERIES[offset : offset + limit]
    return jsonify(
        {
            "nrGalleries": len(MOCK_GALLERIES),
            "galleries": paged_items,
        }
    )


# ==============================================================================
# BELGA 360 ARCHIVE ENDPOINTS
# ==============================================================================


@app.route("/archivenewsobjects", methods=["GET"])
@app.route("/belga360-ws/archivenewsobjects", methods=["GET"])
async def search_360_archive_news_objects():
    """Endpoint for Belga360ArchiveSearchProvider find_async."""
    offset = int(request.args.get("start", 0))
    limit = int(request.args.get("pageSize", 25))
    search_text = request.args.get("searchText", "")

    args = request.args.to_dict()
    from pprint import pprint

    print(f"Search Provided: {search_text}")
    pprint(args)

    paged_items = MOCK_360_ARCHIVE_OBJECTS[offset : offset + limit]
    return jsonify(
        {
            "nrNewsObjects": len(MOCK_360_ARCHIVE_OBJECTS),
            "newsObjects": paged_items,
        }
    )


@app.route("/archivenewsobjects/<news_object_id>", methods=["GET"])
@app.route("/belga360-ws/archivenewsobjects/<news_object_id>", methods=["GET"])
async def get_360_archive_news_object(news_object_id: str):
    """Endpoint for Belga360ArchiveSearchProvider fetch_async & preview lookup."""
    for item in MOCK_360_ARCHIVE_OBJECTS:
        if str(item.get("newsObjectId")) == str(news_object_id):
            return jsonify(item)
    # Fallback
    return jsonify(MOCK_360_ARCHIVE_OBJECTS[0])


@app.route("/archivenewsitems/<int:news_item_id>", methods=["GET"])
@app.route("/belga360-ws/archivenewsitems/<int:news_item_id>", methods=["GET"])
async def get_360_archive_news_item(news_item_id: int):
    """Endpoint for Belga360ArchiveSearchProvider get_detailed_info."""
    items = MOCK_360_ARCHIVE_ITEMS.get(news_item_id, MOCK_360_ARCHIVE_OBJECTS)
    return jsonify(
        {
            "nrNewsObjects": len(items),
            "newsObjects": items,
        }
    )


# ==============================================================================
# BELGA PRESS ENDPOINTS
# ==============================================================================


@app.route("/newsobjects", methods=["GET"])
@app.route("/belgapress/api/newsobjects", methods=["GET"])
async def search_belga_press_news_objects():
    """Endpoint for BelgaPressSearchProvider find_async."""
    offset = int(request.args.get("offset", 0))
    limit = int(request.args.get("count", 25))

    paged_items = MOCK_BELGA_PRESS[offset : offset + limit]
    return jsonify(
        {
            "_meta": {
                "total": len(MOCK_BELGA_PRESS),
            },
            "data": paged_items,
        }
    )


@app.route("/newsobject/<uuid>", methods=["GET"])
@app.route("/belgapress/api/newsobject/<uuid>", methods=["GET"])
async def get_belga_press_news_object(uuid: str):
    """Endpoint for BelgaPressSearchProvider fetch_async."""
    for item in MOCK_BELGA_PRESS:
        if item.get("uuid") == uuid:
            return jsonify(item)
    # Fallback
    return jsonify(MOCK_BELGA_PRESS[0])


# ==============================================================================
# RUNNER
# ==============================================================================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
