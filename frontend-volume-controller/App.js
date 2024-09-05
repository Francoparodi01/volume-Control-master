import React, { useState, useEffect } from 'react';
import { View, Text, FlatList, StyleSheet } from 'react-native';
import Slider from '@react-native-community/slider';

export default function App() {
  const [sessions, setSessions] = useState([]);

  //Ingresamos el ip de nuestra pc, entre las // y el :5000
  useEffect(() => {
    const fetchData = () => {
      fetch('http://192.168.0.147:5000/volume')
        .then(response => response.json())
        .then(data => setSessions(data))
        .catch(error => console.error(error));
    };

    // Llama a la función fetchData por primera vez al cargar el componente
    fetchData();

    // Configura la recarga automática cada 5 segundos
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  const changeVolume = (name, volume) => {
    fetch('http://192.168.0.147:5000/volume', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ name, volume }),
    });
  };

  return (
    <View style={styles.container}>
      <FlatList
        data={sessions}
        keyExtractor={(item) => item.name}
        renderItem={({ item }) => (
          <View style={styles.item}>
            <Text>{item.name}</Text>
            <Slider
              style={{ width: 200, height: 40 }}
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
});
