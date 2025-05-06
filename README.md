<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Alert Table</title>
  <style>
    table {
      border-collapse: collapse;
      width: 100%;
    }
    th, td {
      border: 1px solid #ccc;
      padding: 8px;
      text-align: left;
    }
    th {
      background-color: #f2f2f2;
    }
  </style>
</head>
<body>

  <h2>Alert Summary</h2>

  <table>
    <thead>
      <tr>
        <th>Instance</th>
        <th>Desc</th>
        <th>Alert Name</th>
        <th>Trigger Time</th>
        <th>ACK User</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>srv-web-01</td>
        <td>Web server overload</td>
        <td>CPU Utilization High</td>
        <td>2025-05-06 09:45:23</td>
        <td>alice</td>
      </tr>
      <tr>
        <td>db-main-02</td>
        <td>Database replication delay</td>
        <td>Replication Lag</td>
        <td>2025-05-06 08:13:52</td>
        <td>bob</td>
      </tr>
      <tr>
        <td>cache-redis-03</td>
        <td>Memory usage spike</td>
        <td>Memory Usage Alert</td>
        <td>2025-05-06 10:02:17</td>
        <td>charlie</td>
      </tr>
    </tbody>
  </table>

</body>
</html>
