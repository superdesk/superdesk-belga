import angular from 'angular';

import BelgaSearchPanelController from './BelgaSearchPanelController';

export default angular.module('belga.belgapress', [
])
    .controller('BelgaPressSearchPanelController', BelgaSearchPanelController)
    .run(['$templateCache', ($templateCache) => {
        $templateCache.put(
            'search-panel-belga_press.html',
            require('./views/search-panel.html')
        );
    }]);
