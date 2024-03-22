import * as React from 'react';
import {
    IEditorFieldProps,
    IEventItem,
    IProfileSchemaTypeList,
} from 'superdesk-planning/client/interfaces';

import {ButtonGroup, Button} from 'superdesk-ui-framework/react';
import 'superdesk-planning/client/components/fields/editor/EventRelatedPlannings/style.scss';
import {Row} from 'superdesk-planning/client/components/UI/Form/Row';

import {showModal} from '@superdesk/common';
import EventsRelatedArticlesModal from './EventsRelatedArticlesModal';
import {superdeskApi} from 'superdesk-planning/client/superdeskApi';
import {RelatedArticleComponent} from './RelatedArticleComponent';
import {IArticle} from 'superdesk-api';
import {cleanArticlesFields} from './utils';

interface IProps extends IEditorFieldProps {
    item: IEventItem;
    schema?: IProfileSchemaTypeList;
}

interface IState {
    selectedRelatedArticles: Array<Partial<IArticle>>;
}

export class EditorFieldEventRelatedItems extends React.PureComponent<IProps, IState> {
    constructor(props: IProps) {
        super(props);

        this.state = {
            selectedRelatedArticles: this.props.item.related_items as Array<Partial<IArticle>>,
        };
    }

    componentDidUpdate(prevProps: Readonly<IProps>): void {
        const relatedItemsUpdated = this.props.item.related_items as Array<Partial<IArticle>>;

        if (JSON.stringify(relatedItemsUpdated) !== JSON.stringify(prevProps.item.related_items)) {
            this.setState({
                selectedRelatedArticles: relatedItemsUpdated,
            })
        }
    }

    render() {
        const {gettext} = superdeskApi.localization;
        const disabled = this.props.disabled || this.props.schema?.read_only;

        return (
            <div className='related-plannings'>
                <Row flex={true} noPadding={true}>
                    <label className="InputArray__label side-panel__heading side-panel__heading--big">
                        {gettext('Related Articles')}
                    </label>
                    {disabled ? null : (
                        <ButtonGroup align="end">
                            <Button
                                type="primary"
                                icon="plus-large"
                                text="plus-large"
                                shape="round"
                                size="small"
                                iconOnly={true}
                                onClick={() =>
                                    showModal(({closeModal}) => (
                                        <EventsRelatedArticlesModal
                                            onChange={(value) => {
                                                this.props.onChange(this.props.field, cleanArticlesFields(value));
                                            }}
                                            selectedArticles={this.state.selectedRelatedArticles}
                                            closeModal={() => {
                                                closeModal();
                                            }}
                                        />
                                    ))
                                }
                            />
                        </ButtonGroup>
                    )}
                </Row>
                {(this.props.item.related_items?.length ?? 0) < 1 ? (
                    <Row>
                        <div className="info-box--dashed">
                            <label>{gettext('No related articles yet')}</label>
                        </div>
                    </Row>
                ) : (
                    <ul style={{gap: 4}} className="compact-view list-view">
                        {
                            (this.state.selectedRelatedArticles ?? []).map((relItem) => (
                                <RelatedArticleComponent
                                    editorPreview
                                    key={`${relItem.guid} + ${this.state.selectedRelatedArticles.length}`}
                                    removeArticle={(articleId) => {
                                        this.props.onChange(
                                            this.props.field,
                                            cleanArticlesFields(
                                                [...(this.state.selectedRelatedArticles ?? [])]
                                                    .filter(({guid}) => guid !== articleId)
                                            )
                                        )
                                    }}
                                    article={relItem}
                                />
                            ))
                        }
                    </ul>
                )}
            </div>
        );
    }
}
