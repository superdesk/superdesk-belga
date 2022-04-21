import * as React from 'react';
import BelgaCoverageCarousel from './belga-coverage-carousel';
import {IEditorComponentProps, ISuperdesk} from 'superdesk-api';

const ALLOWED = 'application/vnd.belga.coverage';
const SEPARATOR = ';';

function isAllowedType(event: DragEvent) {
    return !!event.dataTransfer && event.dataTransfer.types.includes(ALLOWED);
}

function getData(event: DragEvent) {
    return event.dataTransfer ? event.dataTransfer.getData(ALLOWED) : '';
}

export function parseIds(value: string | null) : Array<string> {
    return value != null ? value.split(SEPARATOR) : [];
}

function removeId(ids: Array<string>, id: string) : string {
    return ids.filter((_id) => _id !== id).join(SEPARATOR);
}

function addId(ids: Array<string>, id: string) : string {
    return ids.filter((_id) => _id !== id).concat([id]).join(SEPARATOR);
}

export function getBelgaCoverageEditor(superdesk: ISuperdesk): React.StatelessComponent<IEditorComponentProps<string | null, never>> {
    return function BelgaCoverageEditor(props: IEditorComponentProps<string | null, never>) {
        const {gettext} = superdesk.localization;
        const {DropZone} = superdesk.components;
        const ids = parseIds(props.value);

        return (
            <React.Fragment>
                {ids.map((id) => (
                    <div key={id}>
                        <BelgaCoverageCarousel
                            coverageId={id}
                            coverageProvider={props.item.ingest_provider}
                            removeCoverage={props.readOnly ? undefined : () => props.setValue(removeId(ids, id))}
                            superdesk={superdesk}
                        />
                    </div>
                ))}

                <DropZone
                    label={gettext('Add coverage here')}
                    canDrop={isAllowedType}
                    onDrop={(event) => {
                        try {
                            const coverage = JSON.parse(getData(event));

                            props.setValue(addId(ids, coverage.guid));
                        } catch (e) {
                            console.error(e);
                        }
                    }}
                />
            </React.Fragment>
        );
    }
}
