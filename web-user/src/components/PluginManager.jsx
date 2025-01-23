import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  TextField,
  Card,
  CardContent,
  Grid,
  Rating,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  CircularProgress,
  Chip,
  Stack,
  Switch,
  FormControlLabel,
  Tabs,
  Tab,
  Fab,
  Tooltip
} from '@mui/material';
import { Search, Download, Extension, Settings, Add, Delete, Edit } from '@mui/icons-material';
import axios from 'axios';
import Config from '../config/Config';

const PluginManager = () => {
  const [plugins, setPlugins] = useState([]);
  const [userPlugins, setUserPlugins] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedPlugin, setSelectedPlugin] = useState(null);
  const [loading, setLoading] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [tab, setTab] = useState('browse');
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [editPlugin, setEditPlugin] = useState(null);

  useEffect(() => {
    if (tab === 'browse') {
      fetchPlugins();
    } else {
      fetchUserPlugins();
    }
  }, [tab]);

  const fetchPlugins = async (search = '') => {
    setLoading(true);
    try {
      const response = await axios.get(`${Config.backendUrl}/api/plugins/registry${search ? `?q=${search}` : ''}`);
      setPlugins(response.data.plugins);
    } catch (error) {
      console.error('Error fetching plugins:', error);
    }
    setLoading(false);
  };

  const fetchUserPlugins = async () => {
    try {
      const response = await axios.get(`${Config.backendUrl}/api/plugins/user`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });
      setUserPlugins(response.data.plugins);
    } catch (error) {
      console.error('Error fetching user plugins:', error);
    }
  };

  const handleCreatePlugin = async (formData) => {
    try {
      const form = new FormData();
      Object.keys(formData).forEach(key => {
        if (key === 'requirements' || key === 'keywords') {
          form.append(key, JSON.stringify(formData[key]));
        } else {
          form.append(key, formData[key]);
        }
      });

      await axios.post(
        `${Config.backendUrl}/api/plugins/registry`,
        form,
        { 
          headers: { 
            Authorization: `Bearer ${localStorage.getItem('token')}`,
            'Content-Type': 'multipart/form-data'
          } 
        }
      );
      setCreateDialogOpen(false);
      fetchUserPlugins();
    } catch (error) {
      console.error('Error creating plugin:', error);
    }
  };

  const handleDeletePlugin = async (pluginId) => {
    if (window.confirm('Are you sure you want to delete this plugin?')) {
      try {
        await axios.delete(
          `${Config.backendUrl}/api/plugins/registry/${pluginId}`,
          { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } }
        );
        fetchUserPlugins();
      } catch (error) {
        console.error('Error deleting plugin:', error);
      }
    }
  };

  const handleSearch = (event) => {
    setSearchTerm(event.target.value);
    fetchPlugins(event.target.value);
  };

  const handlePluginSelect = async (pluginId) => {
    try {
      const response = await axios.get(`${Config.backendUrl}/api/plugins/registry/${pluginId}`);
      setSelectedPlugin(response.data);
      setDialogOpen(true);
    } catch (error) {
      console.error('Error fetching plugin details:', error);
    }
  };

  const handleInstall = async (pluginId) => {
    try {
      const response = await axios.get(`${Config.backendUrl}/api/plugins/registry/${pluginId}/download`);
      console.log('Plugin installed:', response.data);
      // Add logic to handle successful installation
      fetchPlugins();
    } catch (error) {
      console.error('Error installing plugin:', error);
    }
  };

  const handleTogglePlugin = async (pluginId, enabled) => {
    try {
      const endpoint = enabled ? 'enable' : 'disable';
      await axios.post(`${Config.backendUrl}/api/plugins/registry/${pluginId}/${endpoint}`);
      fetchPlugins();
    } catch (error) {
      console.error('Error toggling plugin:', error);
    }
  };

  return (
    <div maxWidth="lg" sx={{ py: 4 }} className='bg-black'>
        <br />
      <Typography variant="h4" gutterBottom className='text-white'>
        Plugin Manager
      </Typography>

      <Tabs value={tab} onChange={(e, newValue) => setTab(newValue)} sx={{ mb: 4 }}>
        <Tab value="browse" label="Browse Plugins" />
        <Tab value="my-plugins" label="My Plugins" />
      </Tabs>

      {tab === 'browse' ? (
        <>
          <TextField
            fullWidth
            variant="outlined"
            placeholder="Search plugins..."
            value={searchTerm}
            onChange={handleSearch}
            InputProps={{
              startAdornment: <Search color="action" sx={{ mr: 1 }} />
            }}
            sx={{ mb: 4 }}
          />

          {loading ? (
            <Box display="flex" justifyContent="center">
              <CircularProgress />
            </Box>
          ) : (
            <Grid container spacing={3}>
              {plugins.map((plugin) => (
                <Grid item xs={12} sm={6} md={4} key={plugin._id}>
                  <PluginCard 
                    plugin={plugin}
                    onSelect={handlePluginSelect}
                    onInstall={handleInstall}
                    onToggle={handleTogglePlugin}
                  />
                </Grid>
              ))}
            </Grid>
          )}
        </>
      ) : (
        <>
          <Box sx={{ mb: 4, display: 'flex', justifyContent: 'flex-end' }}>
            <Tooltip title="Create New Plugin">
              <Fab color="primary" onClick={() => setCreateDialogOpen(true)}>
                <Add />
              </Fab>
            </Tooltip>
          </Box>

          <Grid container spacing={3}>
            {userPlugins.map((plugin) => (
              <Grid item xs={12} sm={6} md={4} key={plugin._id}>
                <Card>
                  <CardContent>
                    <Typography variant="h6">
                      {plugin.name}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      {plugin.description}
                    </Typography>
                    <Stack direction="row" spacing={1} sx={{ mb: 2 }}>
                      {plugin.keywords.map((keyword) => (
                        <Chip key={keyword} label={keyword} size="small" />
                      ))}
                    </Stack>
                    <Box display="flex" justifyContent="space-between">
                      <Button
                        startIcon={<Edit />}
                        onClick={() => {
                          setEditPlugin(plugin);
                          setCreateDialogOpen(true);
                        }}
                      >
                        Edit
                      </Button>
                      <Button
                        startIcon={<Delete />}
                        color="error"
                        onClick={() => handleDeletePlugin(plugin._id)}
                      >
                        Delete
                      </Button>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </>
      )}

      {/* Plugin Details Dialog */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="md" fullWidth>
        {selectedPlugin && <PluginDetailsDialog plugin={selectedPlugin} onClose={() => setDialogOpen(false)} onInstall={handleInstall} />}
      </Dialog>

      {/* Create/Edit Dialog */}
      <Dialog 
        open={createDialogOpen} 
        onClose={() => {
          setCreateDialogOpen(false);
          setEditPlugin(null);
        }}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {editPlugin ? 'Edit Plugin' : 'Create New Plugin'}
        </DialogTitle>
        <DialogContent>
          <PluginForm
            initialData={editPlugin}
            onSubmit={handleCreatePlugin}
            onCancel={() => {
              setCreateDialogOpen(false);
              setEditPlugin(null);
            }}
          />
        </DialogContent>
      </Dialog>
    </div>
  );
};

const PluginCard = ({ plugin, onSelect, onInstall, onToggle }) => (
  <Card>
    <CardContent>
      <Box display="flex" justifyContent="space-between" alignItems="center">
        <Typography variant="h6">
          {plugin.name}
        </Typography>
        <FormControlLabel
          control={
            <Switch
              checked={plugin.enabled}
              onChange={(e) => onToggle(plugin._id, e.target.checked)}
            />
          }
          label={plugin.enabled ? "Enabled" : "Disabled"}
        />
      </Box>
      <Typography variant="body2" color="text.secondary" gutterBottom>
        {plugin.description}
      </Typography>
      <Stack direction="row" spacing={1} sx={{ mb: 2 }}>
        {plugin.keywords.map((keyword) => (
          <Chip key={keyword} label={keyword} size="small" />
        ))}
      </Stack>
      <Box display="flex" alignItems="center" mb={2}>
        <Rating value={plugin.rating} readOnly precision={0.5} />
        <Typography variant="body2" color="text.secondary" sx={{ ml: 1 }}>
          ({plugin.num_ratings})
        </Typography>
      </Box>
      <Box display="flex" justifyContent="space-between">
        <Button
          startIcon={<Settings />}
          onClick={() => onSelect(plugin._id)}
        >
          Details
        </Button>
        {!plugin.enabled && (
          <Button
            startIcon={<Download />}
            variant="contained"
            onClick={() => onInstall(plugin._id)}
          >
            Install
          </Button>
        )}
      </Box>
    </CardContent>
  </Card>
);

const PluginForm = ({ initialData, onSubmit, onCancel }) => {
  const [formData, setFormData] = useState(initialData || {
    name: '',
    description: '',
    version: '1.0.0',
    plugin_file: null,
    requirements: [],
    keywords: [],
    config: {}
  });

  const handleFileChange = (event) => {
    setFormData({
      ...formData,
      plugin_file: event.target.files[0]
    });
  };

  return (
    <Box component="form" noValidate sx={{ mt: 2 }}>
      <TextField
        fullWidth
        label="Name"
        value={formData.name}
        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
        margin="normal"
      />
      <TextField
        fullWidth
        label="Description"
        value={formData.description}
        onChange={(e) => setFormData({ ...formData, description: e.target.value })}
        margin="normal"
        multiline
        rows={3}
      />
      <TextField
        fullWidth
        label="Version"
        value={formData.version}
        onChange={(e) => setFormData({ ...formData, version: e.target.value })}
        margin="normal"
      />
      <Button
        variant="outlined"
        component="label"
        fullWidth
        sx={{ mt: 2 }}
      >
        Upload Plugin File
        <input
          type="file"
          hidden
          onChange={handleFileChange}
        />
      </Button>
      {formData.plugin_file && (
        <Typography variant="body2" sx={{ mt: 1 }}>
          Selected file: {formData.plugin_file.name}
        </Typography>
      )}
      <TextField
        fullWidth
        label="Requirements (comma-separated)"
        value={formData.requirements.join(', ')}
        onChange={(e) => setFormData({ 
          ...formData, 
          requirements: e.target.value.split(',').map(r => r.trim()) 
        })}
        margin="normal"
      />
      <TextField
        fullWidth
        label="Keywords (comma-separated)"
        value={formData.keywords.join(', ')}
        onChange={(e) => setFormData({ 
          ...formData, 
          keywords: e.target.value.split(',').map(k => k.trim()) 
        })}
        margin="normal"
      />
      <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end', gap: 2 }}>
        <Button onClick={onCancel}>Cancel</Button>
        <Button 
          variant="contained" 
          onClick={() => onSubmit(formData)}
        >
          {initialData ? 'Update' : 'Create'}
        </Button>
      </Box>
    </Box>
  );
};

const PluginDetailsDialog = ({ plugin, onClose, onInstall }) => (
  <>
    <DialogTitle>{plugin.name}</DialogTitle>
    <DialogContent>
      <Typography variant="body1" paragraph>
        {plugin.description}
      </Typography>
      <Typography variant="subtitle1" gutterBottom>
        Author: {plugin.author}
      </Typography>
      <Typography variant="subtitle1" gutterBottom>
        Version: {plugin.version}
      </Typography>
      <Typography variant="subtitle1" gutterBottom>
        Downloads: {plugin.downloads}
      </Typography>
      <Typography variant="subtitle1" gutterBottom>
        Requirements:
      </Typography>
      <Box component="pre" sx={{ bgcolor: 'grey.100', p: 2, borderRadius: 1 }}>
        {plugin.requirements.join('\n')}
      </Box>
    </DialogContent>
    <DialogActions>
      <Button onClick={onClose}>Close</Button>
      {!plugin.enabled && (
        <Button
          startIcon={<Download />}
          variant="contained"
          onClick={() => onInstall(plugin._id)}
        >
          Install
        </Button>
      )}
    </DialogActions>
  </>
);

export default PluginManager; 