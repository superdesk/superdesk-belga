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
        defaultRoute: '/workspace/personal',

        langOverride: {
            'en': {
                'ANPA Category': 'Category',
                'ANPA CATEGORY': 'CATEGORY'
            }
        },

        view: {
            timeformat: 'HH:mm',
            dateformat: 'DD.MM.YYYY',
        },

        features: {
            preview: 1,
            swimlane: {defaultNumberOfColumns: 4},
            editor3: true,
            validatePointOfInterestForImages: false,
            editorHighlights: true,
            planning: true,
            searchShortcut: true,
            editFeaturedImage: true,
        },
        workspace: {
            analytics: true,
            planning: true,
            assignments: true
        }
    };
};
