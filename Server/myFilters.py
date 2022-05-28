
def kalmanFilter(rssi, var = 1.0682, R = 0.01):
  listLen = len(rssi)
  mu = rssi[0][1]
  sigma = var

  output = []
  for i, rssi_n in enumerate(rssi):
    z = rssi_n[1]
    
    # lost track of signal so itterate with last know or start fresh
    if i+1 != listLen:
      if rssi_n[0] != rssi[i+1][0]+1 and (rssi[i+1][0]+1 - rssi_n[0]) < 4:
        for j in range(rssi[i+1][0] - rssi_n[0]):
          muHat = mu
          sigmaHat = sigma + R
          K = sigmaHat/(sigmaHat + var)
          mu = muHat + K*(z - muHat)
          sigma = sigmaHat - K*sigmaHat
      else:
        mu = rssi_n[1]
        sigma = var

    muHat = mu
    sigmaHat = sigma + R

    K = sigmaHat/(sigmaHat + var)

    mu = muHat + K*(z - muHat)
    sigma = sigmaHat - K*sigmaHat

    output.append(mu)

  return output

ALLOWED_MISSED_RECORDS = 3
def runningKalmanFilter(data, rssi, pkGroup, var = 1.0682, R = 0.01):
  z = rssi

  # Deal with lost signals
  if data['pkGroup'] + 1 != pkGroup and not data['pkGroup'] == pkGroup:
    if (pkGroup-data['pkGroup'] <=ALLOWED_MISSED_RECORDS) and pkGroup > data['pkGroup']:
      for i in range(pkGroup-data['pkGroup']):
        muHat = data['mu']
        sigmaHat = data['sigma'] + R
        K = sigmaHat/(sigmaHat + var)
        data['mu'] = muHat + K*(z - muHat)
        data['sigma'] = sigmaHat - K*sigmaHat
    elif (pkGroup-data['pkGroup'] >ALLOWED_MISSED_RECORDS) or pkGroup < data['pkGroup']:
      data['mu'] = rssi
      data['sigma'] = var

  muHat = data['mu']
  sigmaHat = data['sigma'] + R

  K = sigmaHat/(sigmaHat + var)

  data['mu'] = muHat + K*(z - muHat)
  data['sigma'] = sigmaHat - K*sigmaHat

  return data
