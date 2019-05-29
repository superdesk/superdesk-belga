import angular from 'angular';
import {customField} from 'superdesk-core/scripts/apps/fields';

import BelgaSearchPanelController from './BelgaSearchPanelController';
import BelgaCoverageEditor from './belga-coverage-editor';
import BelgaCoveragePreview from './belga-coverage-preview';

export default angular.module('belga.image', [
])
    .controller('BelgaSearchPanel', BelgaSearchPanelController)
    .run(() => {
        customField('belga.coverage', {
            label: 'Belga Coverage',
            editorComponent: BelgaCoverageEditor,
            previewComponent: BelgaCoveragePreview,
        });
    })
    .run(['$templateCache',($templateCache) => {
        $templateCache.put(
            'search-panel-belga_image.html',
            require('./views/search-panel.html')
        );
    }])
;
