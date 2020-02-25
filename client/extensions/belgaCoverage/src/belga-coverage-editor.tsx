import * as React from 'react';
import BelgaCoverageInfo from './belga-coverage-info';
import BelgaCoverageImages from './belga-coverage-images';
import {IEditorComponentProps, ISuperdesk} from 'superdesk-api';

const ALLOWED = 'application/vnd.belga.coverage';

function isAllowedType(event: DragEvent) {
    return !!event.dataTransfer && event.dataTransfer.types.includes(ALLOWED);
}

function getData(event: DragEvent) {
    return event.dataTransfer ? event.dataTransfer.getData(ALLOWED) : '';
}

export function getBelgaCoverageEditor(superdesk: ISuperdesk): React.StatelessComponent<IEditorComponentProps<string | null, never>> {
    return function BelgaCoverageEditor(props: IEditorComponentProps<string | null, never>) {
        if (props.value) {
            return (
                <div>
                    <BelgaCoverageInfo
                        key={props.value}
                        coverageId={props.value}
                        removeCoverage={props.readOnly ? undefined : () => props.setValue(null)}
                        superdesk={superdesk}
                    />
                    <BelgaCoverageImages
                        key={props.value}
                        coverageId={props.value}
                        rendition={'thumbnail'}
                        maxImages={3}
                        superdesk={superdesk}
                    />
                </div>
            );
        }

        const {gettext} = superdesk.localization;
        const {DropZone} = superdesk.components;

        return (
            <DropZone
                label={gettext('Drop coverage here')}
                canDrop={isAllowedType}
                onDrop={(event) => {
                    try {
                        const coverage = JSON.parse(getData(event));

                        props.setValue(coverage.guid);
                    } catch (e) {
                        console.error(e);
                    }
                }}
            />
        );
    }
}
