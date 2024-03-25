import React from 'react';
import {IArticle, IVocabulary} from 'superdesk-api';
import {PreviewFieldType} from 'superdesk-core/scripts/apps/authoring/preview/previewFieldByType';
import {getCustomFieldVocabularies} from 'superdesk-core/scripts/core/helpers/business-logic';
import {getLabelNameResolver} from 'superdesk-core/scripts/apps/workspace/helpers/getLabelForFieldId';
import {appConfig} from 'superdesk-core/scripts/appConfig';
import {gettext} from 'superdesk-core/scripts/core/utils';
import {formatDate} from 'superdesk-core/scripts/core/get-superdesk-api-implementation';
import {getSortedFields} from 'superdesk-core/scripts/apps/authoring/preview/utils';
import {fakeEditor} from './utils';
import {ContentDivider, Heading} from 'superdesk-ui-framework/react';

interface IProps {
    item: Partial<IArticle>;
}

interface IState {
    customFieldVocabularies: Array<IVocabulary>;
    loading: boolean;
}

export class PreviewArticle extends React.PureComponent<IProps, IState> {
    getLabel: (fieldId: string) => string;

    constructor(props: IProps) {
        super(props);

        this.state = {
            customFieldVocabularies: [],
            loading: true,
        }

        this.getLabel = (fieldId: string) => {
            return fieldId;
        };
    }

    componentDidMount(): void {

        getLabelNameResolver().then((getLabel: (fieldId: string) => string) => {
            const customFieldVocabularies = getCustomFieldVocabularies();

            this.getLabel = getLabel;

            this.setState({
                customFieldVocabularies,
                loading: false,
            });
        });
    }

    render() {
        const paddingBlockEnd = {paddingBlockEnd: 4};
        const contentFields = getSortedFields('content', fakeEditor, this.props.item, false, this.state.customFieldVocabularies);
        const contentFieldsFiltered = contentFields.filter((field) => field.id !== 'headline' && field.id !== 'body_html');
        const headlineField = contentFields.find(({id}) => id === 'headline');
        const bodyField = contentFields.find(({id}) => id === 'body_html');

        return (
            <div style={{width: '100%'}} className="preview-content">
                <div>
                    <div style={{flexGrow: 1}} className="css-table">
                        <div className="tr">
                            <div className="td" style={paddingBlockEnd}>
                                <span className="form-label">{gettext('Last modified')}</span>
                            </div>

                            <div
                                className="td"
                                style={{paddingInlineStart: 30, ...paddingBlockEnd}}
                            >
                                {formatDate(new Date(this.props.item.versioncreated))}
                            </div>
                        </div>

                        {
                            getSortedFields('header', fakeEditor, this.props.item, false, this.state.customFieldVocabularies)
                                .map((field) => (
                                    <div key={field.id} className="tr">
                                        <div className="td" style={paddingBlockEnd}>
                                            <span className="form-label">{this.getLabel(field.id)}</span>
                                        </div>

                                        <div
                                            className="td"
                                            style={{paddingInlineStart: 30, ...paddingBlockEnd}}
                                        >
                                            <PreviewFieldType field={field} language={this.props.item.language} />
                                        </div>
                                    </div>
                                ))
                        }
                    </div>
                    <ContentDivider />
                    {
                        headlineField?.id && (
                            <Heading className='pb-2' type='h1'>
                                {headlineField.value}
                            </Heading>
                        )
                    }
                    {
                        bodyField?.id && (
                            <div style={{marginTop: 4}} key={bodyField.id}>
                                <div className="sd-text sd-font-size--medium" dangerouslySetInnerHTML={{__html: bodyField.value as string}} />
                            </div>
                        )
                    }
                    {
                        contentFieldsFiltered
                            .map((field) => (
                                <div key={field.id}>
                                    {
                                        appConfig?.authoring?.preview?.hideContentLabels === true ? <br /> : (
                                            <h3 style={{marginBlockStart: 20, marginBlockEnd: 10}}>
                                                {this.getLabel(field.id)}
                                            </h3>
                                        )
                                    }
                                    <div>
                                        <PreviewFieldType field={field} language={this.props.item.language} />
                                    </div>
                                </div>
                            ))
                    }
                    <br />
                </div>
            </div>
        )
    }
}
