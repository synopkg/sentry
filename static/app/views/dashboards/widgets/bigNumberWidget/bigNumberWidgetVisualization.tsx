import styled from '@emotion/styled';

import {Tooltip} from 'sentry/components/tooltip';
import {defined} from 'sentry/utils';
import type {MetaType} from 'sentry/utils/discover/eventView';
import {getFieldFormatter} from 'sentry/utils/discover/fieldRenderers';
import {useLocation} from 'sentry/utils/useLocation';
import useOrganization from 'sentry/utils/useOrganization';
import {AutoSizedText} from 'sentry/views/dashboards/widgetCard/autoSizedText';
import {NO_DATA_PLACEHOLDER} from 'sentry/views/dashboards/widgets/bigNumberWidget/settings';
import {ErrorPanel} from 'sentry/views/dashboards/widgets/common/errorPanel';
import type {
  Meta,
  StateProps,
  TableData,
} from 'sentry/views/dashboards/widgets/common/types';

export interface Props extends StateProps {
  data?: TableData;
  meta?: Meta;
}

export function BigNumberWidgetVisualization(props: Props) {
  const {data, meta, isLoading, error} = props;

  const location = useLocation();
  const organization = useOrganization();

  if (error) {
    return <ErrorPanel error={error} />;
  }

  // Big Number widgets only show one number, so we only ever look at the first item in the Discover response
  const datum = data?.[0];
  // TODO: Instrument getting more than one data key back as an error

  if (isLoading || !defined(datum) || Object.keys(datum).length === 0) {
    return (
      <AutoResizeParent>
        <AutoSizedText>
          <Deemphasize>{NO_DATA_PLACEHOLDER}</Deemphasize>
        </AutoSizedText>
      </AutoResizeParent>
    );
  }

  const fields = Object.keys(datum);
  const field = fields[0];

  // TODO: meta as MetaType is a white lie. `MetaType` doesn't know that types can be null, but they can!
  const fieldFormatter = meta
    ? getFieldFormatter(field, meta as MetaType, false)
    : value => value.toString();

  const unit = meta?.units?.[field];
  const rendered = fieldFormatter(datum, {
    location,
    organization,
    unit: unit ?? undefined, // TODO: Field formatters think units can't be null but they can
  });

  return (
    <AutoResizeParent>
      <AutoSizedText>
        <NumberContainerOverride>
          <Tooltip title={datum[field]} isHoverable delay={0}>
            {rendered}
          </Tooltip>
        </NumberContainerOverride>
      </AutoSizedText>
    </AutoResizeParent>
  );
}

const AutoResizeParent = styled('div')`
  position: absolute;
  color: ${p => p.theme.headingColor};
  inset: 0;

  * {
    line-height: 1;
    text-align: left !important;
  }
`;

const NumberContainerOverride = styled('div')`
  display: inline-block;

  * {
    text-overflow: clip !important;
    display: inline;
    white-space: nowrap;
  }
`;

const Deemphasize = styled('span')`
  color: ${p => p.theme.gray300};
`;
