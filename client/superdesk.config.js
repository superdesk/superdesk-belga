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
        },
        workspace: {
            analytics: true,
            planning: true,
            assignments: true
        },
        enabledExtensions: {
            markForUser: 1,
            belgaCoverage: 1,
            belga360Archive: 1,
        },
        list: {
            priority: [
                'priority',
                'urgency'
            ],
            firstLine: [
                'wordcount',
                'slugline',
                'highlights',
                'markedDesks',
                'associations',
                'publish_queue_errors',
                'headline',
                'versioncreated'
            ],
            secondLine: [
                'language',
                'profile',
                'state',
                'scheduledDateTime',
                'embargo',
                'update',
                'takekey',
                'signal',
                'broadcast',
                'flags',
                'updated',
                'category',
                'provider',
                'expiry',
                'desk',
                'fetchedDesk',
                'nestedlink',
                'associatedItems',
            ]
        },
    };
};
