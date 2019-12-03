/**
 * This is the default configuration file for the Superdesk application. By default,
 * the app will use the file with the name "superdesk.config.js" found in the current
 * working directory, but other files may also be specified using relative paths with
 * the SUPERDESK_CONFIG environment variable or the grunt --config flag.
 */
module.exports = function(grunt) {
    return {
        apps: [
            'superdesk.analytics',
            'superdesk-planning',
            'belga',
        ],
        importApps: [
            'superdesk-analytics',
            'superdesk-planning',
            '../belga',
        ],
        defaultRoute: '/workspace/monitoring',

        defaultTimezone: 'Europe/Brussels',
        shortTimeFormat: 'HH:mm, DD.MM.YYYY',
        shortDateFormat: 'HH:mm, DD.MM.YYYY',
        shortWeekFormat: 'HH:mm, DD.MM.YYYY',

        startingDay: '1',

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
            editFeaturedImage: false,
            hideCreatePackage: true,
            customAuthoringTopbar: {
                publish: true,
                publishAndContinue: true,
                closeAndContinue: true,
            },
        },
        workspace: {
            analytics: true,
            planning: true,
            assignments: true
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
    };
};
