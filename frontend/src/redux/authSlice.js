import { createSlice } from '@reduxjs/toolkit';

const authSlice = createSlice({
  name: 'auth',
  initialState: {
    user: null,
    isAuthenticated: false,
    role: null,
  },
  reducers: {
    setLogin: (state, action) => {
      state.isAuthenticated = true;
      state.role = action.payload.role;
      state.user = action.payload.user;
    },
    setLogout: (state) => {
      state.isAuthenticated = false;
      state.role = null;
      state.user = null;
    },
  },
});

export const { setLogin, setLogout } = authSlice.actions;
export default authSlice.reducer;
