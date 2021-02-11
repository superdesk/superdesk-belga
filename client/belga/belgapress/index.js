import angular from 'angular';

import BelgaSearchPanelController from './BelgaSearchPanelController';

export default angular.module('belga.belgapress', [
])
    .controller('BelgaSearchPanelController', BelgaSearchPanelController)
    .run(['$templateCache', ($templateCache) => {
        $templateCache.put(
            'search-panel-belga_press.html',
            require('./views/search-panel.html')
        );
    }]);
