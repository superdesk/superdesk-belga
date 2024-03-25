import React, {useState} from 'react';
import {IArticle} from 'superdesk-api';
import {gettext} from 'superdesk-planning/client/utils';
import {IconButton, Label, Spacer} from 'superdesk-ui-framework/react';

interface IProps {
    article: Partial<IArticle>;
    prevSelected?: boolean;
    addArticle?: (article: Partial<IArticle>) => void;
    removeArticle: (id: string) => void;
    setPreview?: (itemToPreview: Partial<IArticle>) => void;
    editorPreview?: boolean;
}

const EDITOR_VIEW_FIELD_WIDTH = '500px';

export const RelatedArticleComponent = ({article, prevSelected, addArticle, removeArticle, setPreview, editorPreview}: IProps) => {
    const [hovered, setHovered] = useState(false);
    const [selected, useSelected] = useState(prevSelected ?? false);

    let listStyles: any = {padding: 6, backgroundColor: 'hsla(214, 13% , 100% , 1)', width: '100%', listStyleType: 'none'};
    if (selected) {
        listStyles = {
            ...listStyles,
            marginTop: 2,
            marginBottom: 2,
            borderColor: '#D9EAF3',
            borderStyle: 'solid',
            borderWidth: '2px',
        }
    } else {
        listStyles = {
            ...listStyles,
            marginTop: 4,
            marginBottom: 4,
            boxShadow: '0 1px 3px rgba(0, 0, 0, 0.16), 0 0 1px rgba(0, 0, 0, 0.1)',
            borderRadius: 3,
        }
    }

    return (
        <li
            style={listStyles}
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
            <Spacer
                h
                gap='16'
                noWrap
                justifyContent='start'
            >
                <div
                    data-test-id="item-type-and-multi-select"
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
                                <IconButton
                                    ariaValue={gettext('Remove')}
                                    icon='trash'
                                    onClick={() => {
                                        removeArticle(article.guid as string);
                                    }}
                                />
                            ) : (
                                <IconButton
                                    ariaValue={gettext('Article Type: text')}
                                    icon='text'
                                    onClick={() => {
                                        //
                                    }}
                                />
                            )
                        )
                    }
                    {
                        !editorPreview && ((hovered && !selected) || selected ? (
                            <div className='icn-btn'>
                                <span className={`sd-checkbox ${selected ? 'checked' : 'unchecked'}`} />
                            </div>
                        ) : (
                            <IconButton
                                ariaValue={gettext('Article Type: text')}
                                icon='text'
                                onClick={() => {
                                    //
                                }}
                            />
                        ))
                    }
                </div>
                <Spacer
                    v
                    gap='8'
                    justifyContent='start'
                    noWrap
                >
                    {/* FIXME: Find a proper fix for the date going outside of the box,
                        instead of having to fix the width to EDITOR_VIEW_FIELD_WIDTH */}
                    <Spacer style={editorPreview ? {width: EDITOR_VIEW_FIELD_WIDTH} : {}} h gap="4" noWrap alignItems='center'>
                        <div
                            style={{
                                fontSize: 14,
                                overflow: 'hidden',
                                textOverflow: 'ellipsis',
                                whiteSpace: 'nowrap',
                            }}
                        >
                            <span>
                                {article.headline}
                            </span>
                        </div>
                        <div style={{whiteSpace: 'nowrap'}}>
                            <span>{new Date(article.versioncreated).toDateString()}</span>
                        </div>
                    </Spacer>
                    <Spacer
                        h
                        gap='4'
                        justifyContent='start'
                        noWrap
                    >
                        <Label text={article.language} style='filled' size='small' type='primary' />
                        <Label text={article.type as string} style='translucent' size='small' type='default' />
                        <Label text={article.state as string} style='filled' size='small' type='sd-green' />
                    </Spacer>
                </Spacer>
            </Spacer>
        </li>
    );
};
