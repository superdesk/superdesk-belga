import React from 'react';
import {gettext} from 'superdesk-core/scripts/core/utils';
import {DropZone} from 'superdesk-core/scripts/core/ui/components/drop-zone';
import {IEditorComponentProps} from 'superdesk-core/scripts/apps/fields';
import BelgaCoverageInfo from './belga-coverage-info';
import BelgaCoverageImages from './belga-coverage-images';

const ALLOWED_TYPES = [
    'application/superdesk.item.graphic',
];

export default class BelgaCoverageEditor extends React.PureComponent<IEditorComponentProps> {
    render() {
        if (this.props.value) {
            return (
                <div>
                    <BelgaCoverageInfo
                        coverageId={this.props.value}
                        removeCoverage={this.props.readOnly ? null : () => this.props.setValue(null)}
                    />
                    <BelgaCoverageImages
                        coverageId={this.props.value}
                        rendition={'thumbnail'}
                        maxImages={3}
                    />
                </div>
            );
        }

        return this.renderDropzone();
    }

    addCoverage(data) {
        const coverage = JSON.parse(data);
        this.props.setValue(coverage.guid);
    }

    renderDropzone() {
        return (
            <DropZone
                text={gettext('Drop coverage here')}
                onDrop={({data}) => this.addCoverage(data)}
                allowedTypes={ALLOWED_TYPES}
            />
        );
    }
}