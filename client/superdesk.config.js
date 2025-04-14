/**
 * This is the default configuration file for the Superdesk application. By default,
 * the app will use the file with the name "superdesk.config.js" found in the current
 * working directory, but other files may also be specified using relative paths with
 * the SUPERDESK_CONFIG environment variable or the grunt --config flag.
 */
module.exports = function(grunt) {
    return {
        apps: [
            //'superdesk.analytics',
            'superdesk-planning',
            'belga',
        ],
        importApps: [
            //'superdesk-analytics',
            'superdesk-planning',
            '../index',
        ],
        defaultRoute: '/workspace/monitoring',

        defaultTimezone: 'Europe/Brussels',
        shortTimeFormat: 'HH:mm, DD.MM.YYYY',
        shortDateFormat: 'HH:mm, DD.MM.YYYY',
        shortWeekFormat: 'HH:mm, DD.MM.YYYY',

        view: {
            timeformat: 'HH:mm',
            dateformat: 'DD.MM.YYYY',
        },

        item_profile: {
            change_profile: 1
        },

        editor: {
            imageDragging: true
        },

        features: {
            preview: 1,
            swimlane: {defaultNumberOfColumns: 4},
            editor3: true,
            validatePointOfInterestForImages: false,
            editorHighlights: true,
            planning: true,
            searchShortcut: true,
            elasticHighlight: true,
            editFeaturedImage: true,
            hideCreatePackage: true,
            noPublishOnAuthoringDesk: true,
            autorefreshContent: true,
            customAuthoringTopbar: {
                publish: true,
                publishAndContinue: true,
                closeAndContinue: true,
            },
            confirmDueDate: true,
            showPublishSchedule: true,
        },

        workspace: {
            analytics: true,
            planning: true,
            assignments: true
        },

        ui: {
            publishEmbargo: false,
            sendEmbargo: false,
        },

        langOverride: {
            'en': {
                'slugline': 'topic',
                'Slugline': 'Topic',
                'SLUGLINE': 'TOPIC',
                'Keywords': 'Storytags',
                'KEYWORDS': 'STORYTAGS',
                'keywords': 'storytags'
                }
            },

        search_cvs: [
            {id: 'belga-keywords', name:'Belga keywords', field: 'subject', list: 'belga-keywords'},
            {id: 'services-products', name:'Packages', field: 'subject', list: 'services-products'},
            {id: 'sources', name:'Sources', field: 'subject', list: 'sources'},
            {id: 'language', name:'Language', field: 'language', list: 'languages'}
        ],

        search: {
            'slugline': 1,
            'headline': 1,
            'unique_name': 1,
            'story_text': 1,
            'byline': 0,
            'keywords': 1,
            'creator': 1,
            'from_desk': 1,
            'to_desk': 1,
            'spike': 1,
            'ingest_provider': 1,
            'marked_desks': 1,
            'scheduled': 1
        },

        list: {
            priority: [
                'urgency'
            ],
            firstLine: [
                'slugline',
                'highlights',
                'markedDesks',
                'headline',
                'wordcount',
                'associations',
                'publish_queue_errors',
                'versioncreated'
            ],
            secondLine: [
                'profile',
                'state',
                'update',
                'scheduledDateTime',
                'embargo',
                'takekey',
                'signal',
                'broadcast',
                'flags',
                'updated',
                'provider',
                {
                    field: 'authors',
                    options: {
                        displayField: 'username',
                        includeRoles: ['CORRESPONDENT', 'AUTHOR'],
                    },
                },
                'desk',
                'fetchedDesk',
                'associatedItems',
                'translations',
            ]
        },
        monitoring: {
            scheduled: {
                sort: {
                    default: { field: 'publish_schedule', order: 'asc' },
                    allowed_fields_to_sort: [ 'publish_schedule' ]
                }
            },
        },
        assignmentsList: {
            firstLine: ['slugline', 'name'],
            secondLine: [
                'priority',
                'state',
                'accepted',
                'content',
                'internal',
                'due_date',
                'desk',
                'genre',
            ],
        }
    };
};
