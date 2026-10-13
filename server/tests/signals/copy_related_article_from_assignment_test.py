from unittest import mock
from copy import deepcopy
from bson import ObjectId

from superdesk import get_resource_service
from superdesk.utc import utcnow
from apps.search_providers.proxy import PROXY_ENDPOINT
from superdesk.tests import utils as test_utils

from planning.types import EventRelatedItem

from belga.signals.copy_related_article_from_assignment import (
    _get_related_content_field_to_use,
    _get_related_items_from_planning_or_event,
    _get_event_related_item_from_search_proxy,
    on_assignment_start_working,
)
from belga.search_providers import Belga360ArchiveSearchProvider

from .. import TestCase


def mock_raise_exception(*args, **kwargs):
    raise Exception("Something went wrong")


SEARCH_PROVIDER_ID = ObjectId()


TEST_EVENTS = [
    dict(
        _id="event_without_related_items",
        dates=dict(
            start="2024-06-30T14:00:00+0000",
            end="2024-06-30T16:00:00+0000",
        ),
        type="event",
    ),
    dict(
        _id="event_with_related_items",
        dates=dict(
            start="2024-06-30T14:00:00+0000",
            end="2024-06-30T16:00:00+0000",
        ),
        type="event",
        related_items=[
            EventRelatedItem(
                guid="item-en-1",
                type="text",
                state="published",
                version="1",
                headline="Test English Headline",
                slugline="test-en-item",
                versioncreated=utcnow(),
                source="sofab",
                search_provider=str(SEARCH_PROVIDER_ID),
                pubstatus="usable",
                language="en",
            ),
            EventRelatedItem(
                guid="item-de-1",
                type="text",
                state="published",
                version="1",
                headline="Test Deutsch Headline",
                slugline="test-de-item",
                versioncreated=utcnow(),
                source="sofab",
                search_provider=str(SEARCH_PROVIDER_ID),
                pubstatus="usable",
                language="de",
            ),
        ],
    ),
]

TEST_EXTERNAL_ITEMS = [
    dict(
        guid="item-en-1",
        type="text",
        state="published",
        version="1",
        headline="Test English Headline",
        slugline="test-en-item",
        versioncreated=utcnow(),
        source="sofab",
        search_provider="abcd",
        pubstatus="usable",
        language="en",
        _fetchable=False,
    ),
    dict(
        guid="item-de-1",
        type="text",
        state="published",
        version="1",
        headline="Test Deutsch Headline",
        slugline="test-de-item",
        versioncreated=utcnow(),
        source="sofab",
        search_provider="abcd",
        pubstatus="usable",
        language="de",
        _fetchable=False,
    ),
]


def mock_search_provider_fetch(guid: str):
    return next(
        (item for item in TEST_EXTERNAL_ITEMS if item.get("guid") == guid), None
    )


class CopyRelatedArticleFromAssignmentTestCase(TestCase):
    def test_get_related_content_field_to_use(self):
        self.assertEqual(
            "belga_related_articles",
            _get_related_content_field_to_use(
                {
                    "schema": {
                        "belga_related_articles": {"type": "related_content"},
                    }
                }
            ),
        )

        # Prefer ``belga_related_articles`` over other ``related_content`` fields
        self.assertEqual(
            "belga_related_articles",
            _get_related_content_field_to_use(
                {
                    "schema": {
                        "slugline": {"type": "text"},
                        "other_articles": {"type": "related_content"},
                        "belga_related_articles": {"type": "related_content"},
                    }
                }
            ),
        )

        # If no ```belga_related_articles```` field, fallback to the first discovered ``related_content`` field
        self.assertEqual(
            "other_articles_a",
            _get_related_content_field_to_use(
                {
                    "schema": {
                        "slugline": {"type": "text"},
                        "other_articles_a": {"type": "related_content"},
                        "other_articles_b": {"type": "related_content"},
                    }
                }
            ),
        )

    async def test_get_related_items_from_planning(self):
        test_events = deepcopy(TEST_EVENTS)
        await test_utils.post_items("events", test_events)

        self.assertEqual(
            [],
            await _get_related_items_from_planning_or_event(
                {
                    "_id": "p1",
                    "related_events": [
                        {"_id": "non_existing_id", "link_type": "primary"}
                    ],
                }
            ),
        )
        self.assertEqual(
            [],
            await _get_related_items_from_planning_or_event(
                {
                    **test_events[0],
                    "related_events": [
                        {"_id": test_events[0]["_id"], "link_type": "primary"}
                    ],
                }
            ),
        )
        self.assertEqual(
            test_events[1]["related_items"],
            await _get_related_items_from_planning_or_event(
                {
                    **test_events[1],
                    "related_events": [
                        {"_id": test_events[1]["_id"], "link_type": "primary"}
                    ],
                }
            ),
        )
        self.assertEqual(
            [test_events[1]["related_items"][0]],
            await _get_related_items_from_planning_or_event(
                {
                    **test_events[1],
                    "related_events": [
                        {"_id": test_events[1]["_id"], "link_type": "primary"}
                    ],
                },
                "en",
            ),
        )
        self.assertEqual(
            [test_events[1]["related_items"][1]],
            await _get_related_items_from_planning_or_event(
                {
                    **test_events[1],
                    "related_events": [
                        {"_id": test_events[1]["_id"], "link_type": "primary"}
                    ],
                },
                "de",
            ),
        )
        self.assertEqual(
            [],
            await _get_related_items_from_planning_or_event(
                {
                    **test_events[1],
                    "related_events": [
                        {"_id": test_events[1]["_id"], "link_type": "primary"}
                    ],
                },
                "fr",
            ),
        )

    async def test_get_related_items_from_event(self):
        test_events = deepcopy(TEST_EVENTS)

        self.assertEqual(
            [], await _get_related_items_from_planning_or_event(test_events[0])
        )

        self.assertEqual(
            test_events[1]["related_items"],
            await _get_related_items_from_planning_or_event(test_events[1]),
        )

        self.assertEqual(
            [test_events[1]["related_items"][0]],
            await _get_related_items_from_planning_or_event(test_events[1], "en"),
        )

        self.assertEqual(
            [test_events[1]["related_items"][1]],
            await _get_related_items_from_planning_or_event(test_events[1], "de"),
        )

        self.assertEqual(
            [], await _get_related_items_from_planning_or_event(test_events[1], "fr")
        )

    async def test_get_event_related_item_from_search_proxy(self):
        # Test validating required arguments returns ``None``
        self.assertIsNone(await _get_event_related_item_from_search_proxy({}))
        self.assertIsNone(
            await _get_event_related_item_from_search_proxy(
                {"search_provider": str(ObjectId())}
            )
        )

        # Make sure exception(s) raised while fetching external item is caught
        search_proxy_service = get_resource_service(PROXY_ENDPOINT)
        self.app.data.insert(
            "search_providers",
            [
                {
                    "_id": SEARCH_PROVIDER_ID,
                    "search_provider": "belga_360archive",
                    "source": "sofab",
                    "config": {},
                    "name": "Test Search Provider",
                }
            ],
        )
        with mock.patch.object(
            search_proxy_service, "fetch_async", side_effect=mock_raise_exception
        ) as mock_fetch:
            external_item = await _get_event_related_item_from_search_proxy(
                {
                    "search_provider": str(ObjectId()),
                    "guid": "non_existing",
                }
            )
            self.assertEqual(mock_fetch.call_count, 1)
            self.assertIsNone(external_item)
        with mock.patch.object(
            Belga360ArchiveSearchProvider,
            "fetch_async",
            side_effect=mock_raise_exception,
        ) as mock_fetch:
            external_item = await _get_event_related_item_from_search_proxy(
                {
                    "search_provider": str(SEARCH_PROVIDER_ID),
                    "guid": "non_existing",
                }
            )
            self.assertEqual(mock_fetch.call_count, 1)
            self.assertIsNone(external_item)

        with mock.patch.object(
            Belga360ArchiveSearchProvider,
            "fetch_async",
            return_value=TEST_EXTERNAL_ITEMS[0],
        ):
            self.assertEqual(
                TEST_EXTERNAL_ITEMS[0],
                await _get_event_related_item_from_search_proxy(
                    {
                        "search_provider": str(SEARCH_PROVIDER_ID),
                        "guid": "item-en-1",
                    }
                ),
            )

    async def test_on_planning_assignment_start_working(self):
        test_events = deepcopy(TEST_EVENTS)
        await test_utils.post_items("events", test_events)
        self.app.data.insert(
            "search_providers",
            [
                {
                    "_id": SEARCH_PROVIDER_ID,
                    "search_provider": "belga_360archive",
                    "source": "sofab",
                    "config": {},
                    "name": "Test Search Provider",
                }
            ],
        )

        content_profile = {
            "schema": {"belga_related_articles": {"type": "related_content"}}
        }
        planning = {
            "type": "planning",
            "related_events": [{"_id": test_events[0]["_id"], "link_type": "primary"}],
        }
        item = {}
        kwargs = dict(
            assignment={},
            planning=planning,
            item=item,
            content_profile=content_profile,
        )

        with mock.patch.object(
            Belga360ArchiveSearchProvider,
            "fetch_async",
            side_effect=mock_search_provider_fetch,
        ):
            await on_assignment_start_working(**kwargs)
            self.assertIsNone(item.get("associations"))

            kwargs["planning"]["related_events"] = [
                {"_id": test_events[1]["_id"], "link_type": "primary"}
            ]
            kwargs["item"] = item = {}
            await on_assignment_start_working(**kwargs)

            self.assertEqual(
                item["associations"]["belga_related_articles--1"],
                TEST_EXTERNAL_ITEMS[0],
            )
            self.assertEqual(
                item["associations"]["belga_related_articles--2"],
                TEST_EXTERNAL_ITEMS[1],
            )

            kwargs["item"] = item = {"language": "en"}
            await on_assignment_start_working(**kwargs)
            self.assertEqual(
                item["associations"]["belga_related_articles--1"],
                TEST_EXTERNAL_ITEMS[0],
            )
            self.assertIsNone(item["associations"].get("belga_related_articles--2"))

            kwargs["item"] = item = {"language": "de"}
            await on_assignment_start_working(**kwargs)
            self.assertEqual(
                item["associations"]["belga_related_articles--1"],
                TEST_EXTERNAL_ITEMS[1],
            )
            self.assertIsNone(item["associations"].get("belga_related_articles--2"))

            kwargs["item"] = item = {"language": "fr"}
            await on_assignment_start_working(**kwargs)
            self.assertIsNone(item.get("associations"))

    async def test_on_event_assignment_start_working(self):
        test_events = deepcopy(TEST_EVENTS)
        self.app.data.insert(
            "search_providers",
            [
                {
                    "_id": SEARCH_PROVIDER_ID,
                    "search_provider": "belga_360archive",
                    "source": "sofab",
                    "config": {},
                    "name": "Test Search Provider",
                }
            ],
        )
        content_profile = {
            "schema": {"belga_related_articles": {"type": "related_content"}}
        }

        event = test_events[0]
        item = {}
        kwargs = dict(
            assignment={},
            planning=event,
            item=item,
            content_profile=content_profile,
        )
        with mock.patch.object(
            Belga360ArchiveSearchProvider,
            "fetch_async",
            side_effect=mock_search_provider_fetch,
        ):
            # Test Event1
            await on_assignment_start_working(**kwargs)
            self.assertIsNone(item.get("associations"))

            # Test Event2
            kwargs["planning"] = test_events[1]
            kwargs["item"] = item = {}
            await on_assignment_start_working(**kwargs)
            self.assertEqual(
                item["associations"]["belga_related_articles--1"],
                TEST_EXTERNAL_ITEMS[0],
            )
            self.assertEqual(
                item["associations"]["belga_related_articles--2"],
                TEST_EXTERNAL_ITEMS[1],
            )

            # Test Event2 in `en`
            kwargs["item"] = item = {"language": "en"}
            await on_assignment_start_working(**kwargs)
            self.assertEqual(
                item["associations"]["belga_related_articles--1"],
                TEST_EXTERNAL_ITEMS[0],
            )
            self.assertIsNone(item["associations"].get("belga_related_articles--2"))

            # Test Event2 in `de`
            kwargs["item"] = item = {"language": "de"}
            await on_assignment_start_working(**kwargs)
            self.assertEqual(
                item["associations"]["belga_related_articles--1"],
                TEST_EXTERNAL_ITEMS[1],
            )
            self.assertIsNone(item["associations"].get("belga_related_articles--2"))

            # Test Event2 in `fr`
            kwargs["item"] = item = {"language": "fr"}
            await on_assignment_start_working(**kwargs)
            self.assertIsNone(item.get("associations"))
