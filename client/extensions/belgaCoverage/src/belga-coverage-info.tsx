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

    constructor(props: IProps) {
        super(props);
        this.state = {loading: true, coverage: null};
    }

    componentDidMount() {
        this.fetchCoverage();
    }

    fetchCoverage() {
        getCoverageInfo(this.props.superdesk, this.props.coverageId)
            .then((coverage) => this.setState({coverage: coverage, loading: false}))
            .catch(() => {
                this.setState({loading: false});
            });
    }

    render() {
        const {Alert, Figure} = this.props.superdesk.components;

        if (this.state.loading) {
            return null;
        }

        return (
            <Figure caption={this.state.coverage?.description || ''}
                onRemove={this.props.removeCoverage}>
                {this.state.coverage == null && (
                    <Alert type="error" message="There was an error when fetching coverage." />
                )}
                {this.state.coverage != null && (
                    <img src={this.state.coverage.iconThumbnailUrl} />
                )}
            </Figure>
        );
    }
}
