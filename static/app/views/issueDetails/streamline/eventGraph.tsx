import styled from '@emotion/styled';

import {BarChart} from 'sentry/components/charts/barChart';
import {t} from 'sentry/locale';
import {space} from 'sentry/styles/space';

export function EventGraph({}: {}) {
  return (
    <GraphWrapper>
      <SummaryContainer>
        <div>
          <Label>{t('Events')}</Label>
          <Count>{459}</Count>
        </div>
        <div>
          <Label>{t('Users')}</Label>
          <Count>{200}</Count>
        </div>
      </SummaryContainer>
      <ChartContainer>
        <BarChart
          height={80}
          series={[
            {
              data: [
                {name: 'something1', value: 120},
                {name: 'something2', value: 200},
                {name: 'something3', value: 150},
                {name: 'something4', value: 80},
                {name: 'something5', value: 70},
                {name: 'something6', value: 110},
              ],
              type: 'bar',
              seriesName: 'something ELSE',
            },
          ]}
        />
      </ChartContainer>
    </GraphWrapper>
  );
}

const SummaryContainer = styled('div')`
  display: grid;
  grid-template-rows: 1fr 1fr;
  align-items: center;
  gap: ${space(1.5)};
  padding: 0 ${space(1)};
  border-right: 1px solid ${p => p.theme.border};
  margin-right: space(1);
`;

const Label = styled('div')`
  font-size: ${p => p.theme.fontSizeSmall};
  color: ${p => p.theme.subText};
  font-weight: ${p => p.theme.fontWeightBold};
  line-height: 1;
`;

const Count = styled('div')`
  font-size: ${p => p.theme.headerFontSize};
  line-height: 1;
`;

const ChartContainer = styled('div')``;

// const GraphDivider = styled(Divider)`
//   height: 100%;
// `;

const GraphWrapper = styled('div')`
  display: grid;
  grid-template-columns: auto auto 1fr;
`;
