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

const logAction = (action, details) => {
  console.log(`[PluginManager] ${action}:`, details);
  // You could also send this to your backend or logging service
};

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
    logAction('Tab Changed', { newTab: tab });
    if (tab === 'browse') {
      fetchPlugins();
    } else {
      fetchUserPlugins();
    }
  }, [tab]);

  const fetchPlugins = async (search = '') => {
    setLoading(true);
    logAction('Fetching Plugins', { searchTerm: search });
    try {
      const response = await axios.get(
        `${Config.backendUrl}/api/plugins/registry${search ? `?q=${search}` : ''}`,
        { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } }
      );
      logAction('Plugins Fetched', { count: response.data.plugins.length });
      console.log('Fetched plugins:', response.data.plugins);
      setPlugins(response.data.plugins);
    } catch (error) {
      logAction('Error Fetching Plugins', { error: error.message });
      console.error('Error fetching plugins:', error);
    }
    setLoading(false);
  };

  const fetchUserPlugins = async () => {
    logAction('Fetching User Plugins', {});
    try {
      const response = await axios.get(`${Config.backendUrl}/api/plugins/user`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });
      logAction('User Plugins Fetched', { count: response.data.plugins.length });
      setUserPlugins(response.data.plugins);
    } catch (error) {
      logAction('Error Fetching User Plugins', { error: error.message });
      console.error('Error fetching user plugins:', error);
    }
  };

  const handleCreatePlugin = async (formData) => {
    logAction('Creating Plugin', { name: formData.name });
    try {
      // Validate required fields
      if (!formData.name || !formData.version || !formData.description || 
          !formData.plugin_file || !formData.main_file) {
        throw new Error('Please fill in all required fields');
      }

      const form = new FormData();
      
      // Handle basic fields
      form.append('name', formData.name);
      form.append('version', formData.version);
      form.append('description', formData.description);
      form.append('plugin_file', formData.plugin_file);
      form.append('main_file', formData.main_file);  // Add main file

      // Handle arrays and objects
      if (Array.isArray(formData.requirements)) {
        form.append('requirements', JSON.stringify(formData.requirements.filter(Boolean)));
      }
      if (Array.isArray(formData.keywords)) {
        form.append('keywords', JSON.stringify(formData.keywords.filter(Boolean)));
      }
      if (formData.config) {
        form.append('config', JSON.stringify(formData.config));
      }

      const response = await axios.post(
        `${Config.backendUrl}/api/plugins/registry`,
        form,
        { 
          headers: { 
            Authorization: `Bearer ${localStorage.getItem('token')}`,
            'Content-Type': 'multipart/form-data'
          } 
        }
      );

      logAction('Plugin Created', { 
        name: formData.name, 
        id: response.data._id 
      });
      
      setCreateDialogOpen(false);
      fetchUserPlugins();
    } catch (error) {
      logAction('Error Creating Plugin', { 
        error: error.message, 
        name: formData.name 
      });
      console.error('Error creating plugin:', error);
      // Re-throw error to be handled by the form
      throw error;
    }
  };

  const handleDeletePlugin = async (pluginId) => {
    logAction('Deleting Plugin', { pluginId });
    if (window.confirm('Are you sure you want to delete this plugin?')) {
      try {
        await axios.delete(
          `${Config.backendUrl}/api/plugins/registry/${pluginId}`,
          { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } }
        );
        logAction('Plugin Deleted', { pluginId });
        fetchUserPlugins();
      } catch (error) {
        logAction('Error Deleting Plugin', { error: error.message, pluginId });
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
    logAction('Installing Plugin', { pluginId });
    try {
      await axios.get(
        `${Config.backendUrl}/api/plugins/registry/${pluginId}/download`,
        { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } }
      );
      logAction('Plugin Installed', { pluginId });
      fetchPlugins();
    } catch (error) {
      logAction('Error Installing Plugin', { error: error.message, pluginId });
      console.error('Error installing plugin:', error);
    }
  };

  const handleTogglePlugin = async (pluginId, enabled) => {
    logAction('Toggling Plugin', { pluginId, enabled });
    try {
      const endpoint = enabled ? 'enable' : 'disable';
      await axios.post(
        `${Config.backendUrl}/api/plugins/registry/${pluginId}/${endpoint}`,
        {},
        { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } }
      );
      logAction('Plugin Toggled', { pluginId, enabled });
      if (tab === 'browse') {
        fetchPlugins();
      } else {
        fetchUserPlugins();
      }
    } catch (error) {
      logAction('Error Toggling Plugin', { error: error.message, pluginId, enabled });
      console.error('Error toggling plugin:', error);
    }
  };

  return (
    <div sx={{ py: 4 }} className='bg-black pt-20 px-10 h-screen'>
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
        {/* <FormControlLabel
          control={
            <Switch
              checked={plugin.enabled}
              onChange={(e) => onToggle(plugin._id, e.target.checked)}
            />
          }
          label={plugin.enabled ? "Enabled" : "Disabled"}
        /> */}
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
        <Button
          startIcon={plugin.enabled ? <Extension /> : <Download />}
          variant="contained"
          onClick={() => plugin.enabled ? 
            onToggle(plugin._id, false) : 
            onInstall(plugin._id)
          }
        >
          {plugin.enabled ? 'Disable' : 'Install'}
        </Button>
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
    main_file: 'main.py',  // Add default main file path
    requirements: [],
    keywords: [],
    config: {}
  });
  const [error, setError] = useState(null);

  const handleFileChange = (event) => {
    setFormData({
      ...formData,
      plugin_file: event.target.files[0]
    });
  };

  const handleSubmit = async () => {
    try {
      setError(null);
      await onSubmit(formData);
    } catch (err) {
      setError(err.message);
    }
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
        label="Main File Path"
        value={formData.main_file}
        onChange={(e) => setFormData({ ...formData, main_file: e.target.value })}
        margin="normal"
        helperText="Path to the main plugin file (e.g., main.py)"
      />
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
      {error && (
        <Typography color="error" sx={{ mt: 2 }}>
          {error}
        </Typography>
      )}
      <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end', gap: 2 }}>
        <Button onClick={onCancel}>Cancel</Button>
        <Button 
          variant="contained" 
          onClick={handleSubmit}
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
      <Box component="pre" sx={{ bgcolor: 'grey.700', p: 2, borderRadius: 1 }}>
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