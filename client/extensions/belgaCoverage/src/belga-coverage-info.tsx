import * as React from 'react';

import {ISuperdesk} from 'superdesk-api';
import {IBelgaCoverage, getCoverageInfo} from './belga-image-api';

interface IProps {
    coverageId: string;
    removeCoverage?: () => void;
    superdesk: ISuperdesk;
}

interface IState {
    loading: boolean;
    coverage: IBelgaCoverage | null;
}

export default class BelgaCoverageAssocation extends React.Component<IProps, IState> {
    readonly state = {loading: true, coverage: null};

    componentDidMount() {
        this.fetchCoverage();
    }

    fetchCoverage() {
        getCoverageInfo(this.props.coverageId)
            .then((coverage) => this.setState({coverage: coverage, loading: false}))
            .catch(() => {
                this.setState({loading: false});
            });
    }

    render() {
        const {components} = this.props.superdesk;

        if (this.state.loading) {
            return null;
        }

        if (this.state.coverage == null) {
            return <components.Alert type="error">{'There was an error when fetching coverage.'}</components.Alert>;
        }

        return (
            <components.Figure caption={this.state.coverage.description}
                onRemove={this.props.removeCoverage}>
                <img src={this.state.coverage.iconThumbnailUrl} />
            </components.Figure>
        );
    }
}
