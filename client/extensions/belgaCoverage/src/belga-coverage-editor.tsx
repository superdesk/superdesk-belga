import * as React from 'react';
import BelgaCoverageInfo from './belga-coverage-info';
import BelgaCoverageImages from './belga-coverage-images';
import {ICustomFieldType, IEditorComponentProps} from 'superdesk-api';

const ALLOWED = 'application/superdesk.item.graphic';

function isAllowedType(event: DragEvent) {
    return !!event.dataTransfer && event.dataTransfer.types.includes(ALLOWED);
}

function getData(event: DragEvent) {
    return event.dataTransfer ? event.dataTransfer.getData(ALLOWED) : '';
}

export const BelgaCoverageEditor: ICustomFieldType['editorComponent'] = (props: IEditorComponentProps) => {
    if (props.value) {
        return (
            <div>
                <BelgaCoverageInfo
                    coverageId={props.value}
                    removeCoverage={props.readOnly ? undefined : () => props.setValue(null)}
                    superdesk={props.superdesk}
                />
                <BelgaCoverageImages
                    coverageId={props.value}
                    rendition={'thumbnail'}
                    maxImages={3}
                    superdesk={props.superdesk}
                />
            </div>
        );
    }

    const {gettext} = props.superdesk.localization;
    const {DropZone} = props.superdesk.components;

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