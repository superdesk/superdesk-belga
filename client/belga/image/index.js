import angular from 'angular';

import BelgaSearchPanelController from './BelgaSearchPanelController';

export default angular.module('belga.image', [
])
    .controller('BelgaImageSearchPanel', BelgaSearchPanelController)
    .run(['$templateCache',($templateCache) => {
        $templateCache.put(
            'search-panel-belga_image.html',
            require('./views/search-panel.html')
        );
    }])
;
