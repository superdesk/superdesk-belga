import React from 'react';

import {IBelgaCoverage, getCoverageInfo} from './belga-image-api';

interface IProps {
    coverageId: string;
    removeCoverage?: () => void;
}

interface IState {
    loading: boolean;
    coverage: IBelgaCoverage;
}

export default class BelgaCoverageAssocation extends React.Component<IProps, IState> {
    readonly state = {loading: true, coverage: null};

    componentDidMount() {
        this.fetchCoverage();
    }

    componentDidUpdate(prevProps) {
        if (prevProps.coverageId !== this.props.coverageId) {
            if (this.props.coverageId) {
                this.setState({loading: true, coverage: null});
                this.fetchCoverage();
            } else {
                this.setState({loading: false, coverage: null})
            }
        }
    }

    fetchCoverage() {
        getCoverageInfo(this.props.coverageId)
            .then((coverage) => this.setState({coverage: coverage, loading: false}))
            .catch(() => {
                this.setState({loading: false});
            });
    }

    render() {
        if (this.state.loading) {
            return null;
        }

        if (this.state.coverage != null) {
            return this.renderCoverage(this.state.coverage);
        }

        return <div>{'There was an error when fetching coverage.'}</div>;
    }

    renderCoverage(coverage: IBelgaCoverage) {
        const inEditor = this.props.removeCoverage != null;
        return (
            <div className={inEditor ? "sd-media-carousel__content" : ''}>
                <figure className="item-association item-association--preview" style={{margin: 0, height: 'inherit'}}>
                    {inEditor && (
                        <button className="item-association__remove-item" onClick={(event) => this.props.removeCoverage()}>
                            <i className="icon-close-small" />
                        </button>
                    )}
                    <div className="item-association__image-container">
                        <div className="item-association__image-overlay" />
                        <img src={coverage.iconThumbnailUrl} />
                    </div>
                </figure>
                <div className={inEditor ? "sd-media-carousel__media-caption" : ''}>{coverage.description}</div>
            </div>
        );

    }
}
