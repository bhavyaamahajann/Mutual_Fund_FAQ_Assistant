export const renderInlineStyles = (line) => {
  const urlRegex = /(https?:\/\/[^\s)]+)/g;
  const parts = [];
  let lastIndex = 0;
  let match;

  while ((match = urlRegex.exec(line)) !== null) {
    if (match.index > lastIndex) {
      parts.push(line.substring(lastIndex, match.index));
    }
    parts.push(
      <a 
        key={match.index} 
        href={match[1]} 
        target="_blank" 
        rel="noreferrer" 
        style={{ color: '#854d0e', textDecoration: 'underline', wordBreak: 'break-all' }}
      >
        {match[1]}
      </a>
    );
    lastIndex = urlRegex.lastIndex;
  }

  if (lastIndex < line.length) {
    parts.push(line.substring(lastIndex));
  }

  return parts.length > 0 ? parts : line;
};

export const renderTable = (table, key) => {
  return (
    <div key={key} className="table-responsive" style={{ margin: '12px 0', overflowX: 'auto', borderRadius: '6px', border: '1px solid #e5e7eb' }}>
      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.8rem', fontFamily: 'sans-serif' }}>
        <thead>
          <tr style={{ backgroundColor: '#f9fafb', borderBottom: '1px solid #e5e7eb' }}>
            {table.headers.map((header, idx) => {
              const align = table.alignments[idx] || 'left';
              return (
                <th 
                  key={idx} 
                  style={{ 
                    padding: '8px 10px', 
                    textAlign: align, 
                    fontWeight: '600', 
                    color: '#374151',
                    borderBottom: '1px solid #e5e7eb', 
                    borderRight: idx < table.headers.length - 1 ? '1px solid #e5e7eb' : 'none' 
                  }}
                >
                  {header}
                </th>
              );
            })}
          </tr>
        </thead>
        <tbody>
          {table.rows.map((row, rowIdx) => (
            <tr 
              key={rowIdx} 
              style={{ 
                borderBottom: rowIdx < table.rows.length - 1 ? '1px solid #e5e7eb' : 'none', 
                backgroundColor: rowIdx % 2 === 0 ? '#ffffff' : '#f9fafb' 
              }}
            >
              {row.map((cell, cellIdx) => {
                const align = table.alignments[cellIdx] || 'left';
                return (
                  <td 
                    key={cellIdx} 
                    style={{ 
                      padding: '8px 10px', 
                      textAlign: align, 
                      color: '#4b5563',
                      borderRight: cellIdx < row.length - 1 ? '1px solid #e5e7eb' : 'none' 
                    }}
                  >
                    {cell}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export const cleanMessageText = (text) => {
  if (!text) return '';
  // Remove "Last updated from sources: ..." (case-insensitive, including any leading newlines)
  let cleaned = text.replace(/\n*Last updated from sources:[\s\S]*$/i, '');
  // Remove "Source: ..." (case-insensitive, including any leading newlines)
  cleaned = cleaned.replace(/\n*Source:[\s\S]*$/i, '');
  return cleaned.trim();
};

export const renderMessageText = (text) => {
  if (!text) return null;

  const lines = text.split('\n');
  const elements = [];
  let currentTable = null;

  const parseAlignments = (line) => {
    const parts = line.split('|').slice(1, -1);
    return parts.map(part => {
      const trimmed = part.trim();
      if (trimmed.startsWith(':') && trimmed.endsWith(':')) return 'center';
      if (trimmed.endsWith(':')) return 'right';
      return 'left';
    });
  };

  const parseRow = (line) => {
    return line.split('|').slice(1, -1).map(part => part.trim());
  };

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const isTableLine = line.trim().startsWith('|');

    if (isTableLine) {
      if (!currentTable) {
        currentTable = {
          headers: parseRow(line),
          rows: [],
          alignments: []
        };
      } else if (line.includes('---')) {
        currentTable.alignments = parseAlignments(line);
      } else {
        currentTable.rows.push(parseRow(line));
      }
    } else {
      if (currentTable) {
        elements.push(renderTable(currentTable, elements.length));
        currentTable = null;
      }
      if (line.trim()) {
        elements.push(
          <p key={elements.length} style={{ margin: '0 0 8px 0', whiteSpace: 'pre-line', lineHeight: '1.4' }}>
            {renderInlineStyles(line)}
          </p>
        );
      } else {
        elements.push(<div key={elements.length} style={{ height: '8px' }} />);
      }
    }
  }

  if (currentTable) {
    elements.push(renderTable(currentTable, elements.length));
  }

  return <div>{elements}</div>;
};
