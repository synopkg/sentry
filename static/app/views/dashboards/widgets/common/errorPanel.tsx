import styled from '@emotion/styled';

import {IconWarning} from 'sentry/icons';
import {space} from 'sentry/styles/space';
import {DEEMPHASIS_COLOR_NAME} from 'sentry/views/dashboards/widgets/bigNumberWidget/settings';
import type {StateProps} from 'sentry/views/dashboards/widgets/common/types';

interface Props {
  error: StateProps['error'];
}

export function ErrorPanel({error}: Props) {
  return (
    <Panel>
      <IconWarning color={DEEMPHASIS_COLOR_NAME} size="lg" />
      <span>{error?.toString()}</span>
    </Panel>
  );
}

const Panel = styled('div')<{height?: string}>`
  position: absolute;
  inset: 0;

  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: ${space(0.5)};

  overflow: hidden;

  color: ${p => p.theme[DEEMPHASIS_COLOR_NAME]};
  font-size: ${p => p.theme.fontSizeExtraLarge};
`;
