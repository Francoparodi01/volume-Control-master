import React, { useState, useEffect } from 'react';
import { View, Text, FlatList, TextInput, Button, StyleSheet, Image } from 'react-native';
import Slider from '@react-native-community/slider';

export default function App() {
  const [sessions, setSessions] = useState([]);
  const [ipAddress, setIpAddress] = useState('192.168.0.147');
  const [intervalId, setIntervalId] = useState(null);

  const fetchData = () => {
    fetch(`http://${ipAddress}:5000/volume`)
      .then(response => response.json())
      .then(data => {
        const updatedSessions = data.map(session => ({
          ...session,
          icon: session.icon ? `data:image/png;base64,${session.icon}` : null,
        }));
        setSessions(updatedSessions);
      })
      .catch(error => console.error(error));
  };

  useEffect(() => {
    fetchData();
    const id = setInterval(fetchData, 5000);
    setIntervalId(id);
    return () => clearInterval(id);
  }, [ipAddress]);

  const changeVolume = (name, volume) => {
    fetch(`http://${ipAddress}:5000/volume`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ name, volume }),
    });
  };

  const handleIpChange = () => {
    if (intervalId) clearInterval(intervalId);
    fetchData();
  };

  return (
    <View style={styles.container}>
      <TextInput
        style={styles.input}
        placeholder="Ingrese IP del servidor"
        value={ipAddress}
        onChangeText={text => setIpAddress(text)}
      />
      <Button title="Cambiar IP" onPress={handleIpChange} />
      
      <FlatList
        data={sessions}
        keyExtractor={(item, index) => `${item.name}-${index}`}
        renderItem={({ item }) => (
          <View style={styles.item}>
            {item.icon && (
              <Image
                source={{ uri: item.icon }} // Ahora es una cadena base64
                style={styles.icon}
              />
            )}
            <Text>{item.name}</Text>
            <Slider
              style={styles.slider}
              minimumValue={0}
              maximumValue={1}
              value={item.volume}
              onValueChange={(value) => changeVolume(item.name, value)}
            />
          </View>
        )}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 50,
  },
  item: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 20,
  },
  icon: {
    width: 30,
    height: 30,
    marginRight: 10,
  },
  slider: {
    width: 200,
    height: 40,
  },
  input: {
    height: 40,
    borderColor: 'gray',
    borderWidth: 1,
    marginBottom: 20,
    paddingHorizontal: 10,
    width: '80%',
  },
});
