import * as React from 'react';
import BelgaCoverageCarousel from './belga-coverage-carousel';
import {ICommonFieldConfig, IEditorComponentProps, ISuperdesk} from 'superdesk-api';

const ALLOWED = 'application/vnd.belga.coverage';
const SEPARATOR = ';';

function isAllowedType(event: DragEvent | undefined) {
    return event?.dataTransfer?.types.includes(ALLOWED) || false;
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

type IProps = IEditorComponentProps<string, ICommonFieldConfig, never>;

export function getBelgaCoverageEditor(superdesk: ISuperdesk) {
    class BelgaCoverageEditor extends React.PureComponent<IProps> {
        render() {
            const {gettext} = superdesk.localization;
            const {DropZone} = superdesk.components;
            const ids = parseIds(this.props.value);
            const Container = this.props.container;

            return (
                <Container>
                    {ids.map((id) => (
                        <div key={id}>
                            <BelgaCoverageCarousel
                                coverageId={id}
                                removeCoverage={this.props.readOnly ? undefined : () => this.props.onChange(removeId(ids, id))}
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

                                this.props.onChange(addId(ids, coverage.extra.bcoverage));
                            } catch (e) {
                                console.error(e);
                            }
                        }}
                    />
                </Container>
            );
        }
    }

    return BelgaCoverageEditor;
}
