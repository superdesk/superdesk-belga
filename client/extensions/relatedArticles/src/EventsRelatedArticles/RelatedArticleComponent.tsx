import React, {useState} from 'react';
import {IArticle} from 'superdesk-api';
import {gettext} from 'superdesk-planning/client/utils';
import {IconButton, Label} from 'superdesk-ui-framework/react';

interface IProps {
    article: Partial<IArticle>;
    prevSelected?: boolean;
    addArticle?: (article: Partial<IArticle>) => void;
    removeArticle: (id: string) => void;
    setPreview?: (itemToPreview: Partial<IArticle>) => void;
    editorPreview?: boolean;
}

export const RelatedArticleComponent = ({article, prevSelected, addArticle, removeArticle, setPreview, editorPreview}: IProps) => {
    const [hovered, setHovered] = useState(false);
    const [selected, useSelected] = useState(prevSelected ?? false);

    let styles = {};
    if (selected) {
        styles = {
            ...styles,
            borderColor: '#D9EAF3',
            borderStyle: 'solid',
            borderWidth: '2px',
        }
    }

    return (
        <li
            style={selected ? {marginTop: 2, marginBottom: 2} : {marginTop: 4, marginBottom: 4}}
            className="list-item-view actions-visible"
            draggable
            tabIndex={0}
            data-test-id="article-item"
            onClick={(e) => {
                e.preventDefault();
                e.stopPropagation();

                setPreview?.(article);
            }}
            onMouseLeave={(e) => {
                setHovered(false);

                e.stopPropagation();
                e.preventDefault();
            }}
            onMouseOver={(e) => {
                setHovered(true);

                e.stopPropagation();
                e.preventDefault();
            }}
        >
            <div className="media-box media-text" style={styles}>
                <div>
                    <span className="state-border" />
                    <div
                        className="list-field type-icon sd-monitoring-item-multi-select-checkbox"
                        data-test-id="item-type-and-multi-select"
                        style={{lineHeight: 0}}
                        onClick={(e) => {
                            e.stopPropagation();
                            e.preventDefault();

                            if (editorPreview) {
                                removeArticle(article.guid as string)
                            } else {
                                useSelected(!selected);
                                selected ? removeArticle(article.guid as string) : addArticle?.(article);
                            }
                        }}
                    >
                        <span className="a11y-only">{gettext('Article Type: {{articleType}}', {articleType: article.type})}</span>
                        {
                            editorPreview && (
                                hovered ? (
                                    <div className='strict-isolation'>
                                        <IconButton
                                            ariaValue={gettext('Remove')}
                                            icon='trash'
                                            onClick={() => {
                                                removeArticle(article.guid as string);
                                            }}
                                        />
                                    </div>
                                ) : (
                                    <i
                                        className="filetype-icon-text"
                                        title={gettext("Article Type: text")}
                                        aria-label={gettext('Article Type text')}
                                        aria-hidden="true"
                                    />
                                )
                            )
                        }
                        {
                            !editorPreview && ((hovered && !selected) || selected ? (
                                <button
                                    role="checkbox"
                                    aria-checked="true"
                                    aria-label="bulk actions"
                                    data-test-id="multi-select-checkbox"
                                >
                                    <span className={`sd-checkbox ${selected ? 'checked' : 'unchecked'}`} />
                                </button>
                            ) : (
                                <i
                                    className="filetype-icon-text"
                                    title={gettext("Article Type: text")}
                                    aria-label={gettext('Article Type text')}
                                    aria-hidden="true"
                                />
                            ))
                        }
                    </div>
                    <div
                        className="item-info"
                        style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}
                    >
                        <div
                            style={{flexGrow: 1, flexDirection: 'column', overflow: 'hidden'}}
                        >
                            <div className="line">
                                <span className="item-heading">{article.headline}</span>
                                <div className="highlights-box" />
                                <div className="highlights-box" />
                                <time title={`${article.versioncreated}`}>{new Date(article.versioncreated).toDateString()}</time>
                            </div>
                            <div className="line">
                                <Label text={article.language} style='filled' size='small' type='primary' />
                                <Label text={article.type as string} style='translucent' size='small' type='default' />
                                <Label text={article.state as string} style='filled' size='small' type='sd-green' />
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </li>
    );
};
