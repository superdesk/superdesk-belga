import React from 'react';
import {gettext} from 'superdesk-core/scripts/core/utils';
import {DropZone} from 'superdesk-core/scripts/core/ui/components/drop-zone';
import {IEditorComponentProps} from 'superdesk-core/scripts/apps/fields';
import BelgaCoverageInfo from './belga-coverage-info';
import BelgaCoverageImages from './belga-coverage-images';

const ALLOWED = 'application/superdesk.item.graphic';

function isAllowedType(event: DragEvent) {
    return event.dataTransfer.types.includes(ALLOWED);
}

function getData(event: DragEvent) {
    return event.dataTransfer.getData(ALLOWED);
}

export default function BelgaCoverageEditor(props: IEditorComponentProps) {
    if (props.value) {
        return (
            <div>
                <BelgaCoverageInfo
                    coverageId={props.value}
                    removeCoverage={props.readOnly ? null : () => props.setValue(null)}
                />
                <BelgaCoverageImages
                    coverageId={props.value}
                    rendition={'thumbnail'}
                    maxImages={3}
                />
            </div>
        );
    }

    return (
        <DropZone
            label={gettext('Drop coverage here')}
            canDrop={isAllowedType}
            onDrop={(event) => {
                const coverage = JSON.parse(getData(event));

                props.setValue(coverage.guid);
            }}
        />
    );
}